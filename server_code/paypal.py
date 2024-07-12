import anvil.server
import anvil.secrets
import anvil.http
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.users

from .helpers import get_users_with_permission, validate_user, usermap_row_to_dict
from .emails import notify_paid


# https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions_create
if anvil.server.get_app_origin() is None or 'debug' in anvil.server.get_app_origin():
    TOKEN_URL = 'https://api-m.sandbox.paypal.com/v1/oauth2/token'
    SUBSCRIPTION_URL = 'https://api-m.sandbox.paypal.com/v1/billing/subscriptions'
    # TOKEN_URL = 'https://api.paypal.com/v1/oauth2/token'
    # SUBSCRIPTION_URL = 'https://api.paypal.com/v1/billing/subscriptions'
else:
    TOKEN_URL = 'https://api.paypal.com/v1/oauth2/token'
    SUBSCRIPTION_URL = 'https://api.paypal.com/v1/billing/subscriptions'

def get_paypal_auth(tenant, client_id=None, client_secret=None):
    import json
    
    client_id = client_id or anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_client_id'])
    client_secret = client_secret or anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_secret'])
    
    try:
        auth_response = anvil.http.request(
            TOKEN_URL,
            method="POST",
            username=client_id,
            password=client_secret,
            headers={
                'Accept': 'application/json'
            },
            data={'grant_type': 'client_credentials'}
        )
        # print(auth_response.get_bytes())
        auth_response = json.loads(auth_response.get_bytes().decode('utf-8'))
        access_token = auth_response['access_token']
        
        return access_token
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")
        print(e.content.get_bytes())
        raise anvil.http.HttpError(e.status, e.content)


def get_subscriptions(tenant, subscription_id, access_token=None, verbose=False):
    """Get all info for a subscription id."""
    import datetime as dt
    
    if not subscription_id:
        return None, None, None
    import requests
    access_token = access_token or get_paypal_auth(tenant)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    subscription_detail_response = requests.get(f'{SUBSCRIPTION_URL}/{subscription_id}', headers=headers)
    if verbose:
        print(subscription_detail_response.json())
    try:
        status = subscription_detail_response.json()['status']
        last_payment = dt.datetime.fromisoformat(
            subscription_detail_response.json()['billing_info']['last_payment']['time'].replace("Z", "+00:00")
        ).date()
        payment_amt = float(subscription_detail_response.json()['billing_info']['last_payment']['amount']['value'])
    except KeyError:
        status = None
        last_payment = None
        payment_amt = None
    return status, last_payment, payment_amt


def check_sub(tenant_id, user_row):
    # TODO: deprecate this in favor of a webhook of a subscription expiring
    # from dateutil.relativedelta import relativedelta
    # import datetime as dt
    tenant = app_tables.tenants.get_by_id(tenant_id)
    usermap = app_tables.usermap.get(tenant=tenant, user=user_row)

    if not usermap:
        return None

    status, last_payment, payment_amt = get_subscriptions(tenant, usermap['paypal_sub_id'])
    usermap['payment_status'] = status
    usermap['fee'] = payment_amt


@anvil.server.callable(require_user=True)
def create_sub(tenant_id, plan_id):
    # TODO: make this flexible for user that is sent.
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    access_token = get_paypal_auth(tenant)

    try:
        # Don't specify an email, in case they want to pay with a diff email.
        # Use the subscription id to match them up.
        response = anvil.http.request(
            SUBSCRIPTION_URL,
            method='POST',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            },
            data={
                'plan_id': plan_id,
                'application_context': {
                    # TODO: these should be app pages. Webhooks are set up separately.
                    'return_url': anvil.server.get_app_origin() + '/#app/profile',
                    'cancel_url': anvil.server.get_app_origin() + '/#app/profile'
                }
            },
            json=True
        )
        
        plan = [i for i in tenant['paypal_plans'] if i['id'] == plan_id][0]
        
        usermap['fee'] = plan['amt']
        usermap['paypal_sub_id'] = response['id']
        # TODO: also return usermap_row_to_dict
        membermap = usermap_row_to_dict(usermap)
        if 'see_members' not in permissions:
            membermap['notes'] = ''
        
        return membermap, response['links'][0]['href']
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")
        print(plan_id)
        raise anvil.http.HttpError(e.status, e.content)


@anvil.server.http_endpoint('/capture-sub', methods=['POST'])
def capture_sub(**params):
    verify_paypal_webhook(anvil.server.request.headers, anvil.server.request.body_json)
    
    usermap = app_tables.usermap.get(paypal_sub_id=params['subscription_id'])
    usermap['roles'] = [i for i in usermap['roles'] if i['name'] != 'Applicant']
    member_role = app_tables.roles.get(tenant=usermap['tenant'], name='Member')
    
    if member_role not in usermap['roles']:
        usermap['roles'] = usermap['roles'] + member_role
    
    print(usermap['user']['email'] + ' has just paid. Sending email to screeners.')
    
    screeners = get_users_with_permission(None, 'see_members', usermap['tenant'])
    for screener in screeners:
        print('Sending email to : ' + screener['user']['email'])
        notify_paid(screener['user'], usermap['user'])
    return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#profile'})


def verify_paypal_webhook(request_headers, request_json):
    from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
    from paypalcheckoutsdk.notifications import WebhookEvent

    environment = SandboxEnvironment(client_id='YOUR_PAYPAL_CLIENT_ID', client_secret='YOUR_PAYPAL_CLIENT_SECRET')
    client = PayPalHttpClient(environment)

    paypal_transmission_id = request_headers['Paypal-Transmission-Id']
    paypal_transmission_time = request_headers['Paypal-Transmission-Time']
    paypal_transmission_sig = request_headers['Paypal-Transmission-Sig']
    cert_url = request_headers['Paypal-Cert-Url']
    auth_algo = request_headers['Paypal-Auth-Algo']

    verification_status = WebhookEvent.verify(
        transmission_id=paypal_transmission_id,
        timestamp=paypal_transmission_time,
        webhook_id='YOUR_WEBHOOK_ID',  # Replace with your webhook ID
        event_body=request_json,
        cert_url=cert_url,
        actual_sig=paypal_transmission_sig,
        auth_algo=auth_algo,
        client=client
        )
    return verification_status


@anvil.server.http_endpoint('/cancel-sub')
def cancel_sub(**params):
    row = app_tables.users.get(paypal_sub_id=params['subscription_id'])
    row['paypal_sub_id'] = None
    return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#profile'})


#%% Scheduled Task -------------------------------
@anvil.server.background_task
def calc_rev12():
    for tenant in app_tables.tenants.search():
        tenantfin = app_tables.finances.get(tenant=tenant)
        total_rev = 0
        for user_ref in app_tables.users.search(tenant=tenant, fee=q.not_(None), good_standing=True):
            total_rev += user_ref['fee']*0.97-0.3
        tenantfin['rev_12'] = total_rev
        total_rev = 0
        for user_ref in app_tables.users.search(tenant=tenant, fee=q.not_(None), good_standing=True, payment_status='ACTIVE'):
            total_rev += user_ref['fee']*0.97-0.3
        tenantfin['rev_12_active'] = total_rev
