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
    headers = anvil.server.request.headers
    print(headers)
    body = anvil.server.request.body_json
    raw_body = anvil.server.request.body.get_bytes().decode('utf-8')
    print(raw_body)

    listen_events = ['BILLING.SUBSCRIPTION.ACTIVATED',
                     'BILLING.SUBSCRIPTION.EXPIRED',
                     'BILLING.SUBSCRIPTION.UPDATED']
    if body['event_type'] not in listen_events:
        print(f"not interested in this event: {body['event_type']}")
        return anvil.server.HttpResponse(200)

    usermap = app_tables.usermap.get(paypal_sub_id=body['resource']['id'])
    # if not usermap:
    #     return anvil.server.HttpResponse(400)
    
    if not verify_paypal_webhook(None, headers, raw_body):
        print('Webhook not verified.')
        return anvil.server.HttpResponse(400)
    print('Webhook verified.')
    
    # anvil.server.launch_background_task('update_subscription', headers, raw_body)
    # update_subscription(headers, raw_body)
    
    if body['event_type'] in listen_events:
        print(body['resource']['status'])
        print(body['resource']['id'])
        print(body['resource']['plan_id']) # TODO: match it up later with plan roles.
    return anvil.server.HttpResponse(200)


@anvil.server.background_task
def update_subscription(headers, raw_body):
    pass
    # TODO: look for status 'EXPIRED' to remove roles.
    # TODO: look for status 'ACTIVE' to add roles.
    # everything else just update
    # usermap = app_tables.usermap.get(paypal_sub_id=params['subscription_id'])
    # usermap['roles'] = [i for i in usermap['roles'] if i['name'] != 'Applicant']
    # member_role = app_tables.roles.get(tenant=usermap['tenant'], name='Member')
    
    # if member_role not in usermap['roles']:
    #     usermap['roles'] = usermap['roles'] + member_role
    
    # print(usermap['user']['email'] + ' has just paid. Sending email to screeners.')
    
    # screeners = get_users_with_permission(None, 'see_members', usermap['tenant'])
    # for screener in screeners:
    #     print('Sending email to : ' + screener['user']['email'])
    #     notify_paid(screener['user'], usermap['user'])
    # return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#profile'})


def verify_paypal_webhook(tenant, headers, body):
    import zlib
    import hmac
    import hashlib
    import base64
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from Crypto.Signature import pkcs1_15
    
    transmission_id = headers['paypal-transmission-id']
    timestamp = headers['paypal-transmission-time']
    crc = zlib.crc32(body.encode('utf-8'))
    WEBHOOK_ID = 'WEBHOOK_ID'
    
    message = f"{transmission_id}|{timestamp}|{WEBHOOK_ID}|{crc}"

    signature = base64.b64decode(headers['paypal-transmission-sig'])
    
    cert_pem = get_certificate(tenant, headers['paypal-cert-url'])
    cert_key = RSA.import_key(cert_pem)
    
    h = SHA256.new(message.encode('utf-8'))

    return pkcs1_15.new(cert_key).verify(h, signature)
    # try:
    #     pkcs1_15.new(cert_key).verify(h, signature)
    #     return True
    # except (ValueError, TypeError):
    #     return False
    
    # verifier = hmac.new(cert_pem.encode(), message.encode(), hashlib.sha256)
    # return hmac.compare_digest(verifier.digest(), signature)


def get_certificate(tenant, url):
    import requests
    
    if tenant and tenant['paypal_webhook_certificate']:
        return tenant['paypal_webhook_certificate']
    else:
        response = requests.get(url)
        cert_data = response.text
        if tenant:
            tenant['paypal_webhook_certificate'] = cert_data
        return cert_data


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
