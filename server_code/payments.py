import anvil.server
import anvil.secrets
import anvil.http
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.users

from .helpers import get_users_with_permission, validate_user

# https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions_create
from . import authorisation
from .authorisation import authorisation_required

authorisation.set_config(get_roles='usermap', tenanted=True)



def get_paypal_auth(tenant):
    import requests
    client_id = tenant['paypal_client_id']
    client_secret = tenant['paypal_secret']
    
    auth_response = requests.post('https://api.paypal.com/v1/oauth2/token', 
                                auth=(client_id, client_secret), 
                                headers={'Accept': 'application/json', 'Accept-Language': 'en_US'}, 
                                data={'grant_type': 'client_credentials'})
    
    auth_response_json = auth_response.json()
    access_token = auth_response_json['access_token']
    return access_token


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
    subscription_detail_response = requests.get(f'https://api.paypal.com/v1/billing/subscriptions/{subscription_id}', headers=headers)
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


@anvil.server.callable(require_user=True)
def create_sub(tenant_id, plan_id):
    # import requests
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    access_token = get_paypal_auth(tenant)

    try:
        response = anvil.http.request(
            'https://api.paypal.com/v1/billing/subscriptions',
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
        
        # TODO: move this to the webhook endpoint
        plans = tenant['paypal_plans']
        plan = [i for i in plans if i['plan_id'] == plan_id][0]
        usermap['fee'] = plan['plan_amt']
        
        usermap['paypal_sub_id'] = response['id']
        return response['links'][0]['href']
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")


@anvil.server.http_endpoint('/capture-sub')
def capture_sub(**params):
    # TODO: use fake paypal to test this
    # TODO: secure this
    # TODO: use anvil.server.session.get('tenant_id', None)
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


def notify_paid(user_ref, applicant):
    """Notify the screeners that someone paid."""
    print('Sending email.')
    msg_body = f"""
    <p>Hi {user_ref['first_name']}!</p>

    <p>You are getting this message because an applicant: 
    {applicant['first_name'] + ' ' + applicant['last_name']} ({applicant['email']}) has just paid.</p>

    <p>Regards,</p>
    <p>NotAlone App</p>
    """
    anvil.email.send(
        to=user_ref['email'],
        from_address='noreply',
        from_name="NotAlone",
        subject="Applicant Paid",
        html=msg_body
    )


@anvil.server.http_endpoint('/cancel-sub')
def cancel_sub(**params):
    row = app_tables.users.get(paypal_sub_id=params['subscription_id'])
    row['paypal_sub_id'] = None
    return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#profile'})


@anvil.server.callable(require_user=True)
@authorisation_required('see_members')
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


@anvil.server.callable(require_user=True)
@authorisation_required('edit_members')
def notify_payment(user_ref, tenant=None):
    """Notify the member they need to make a payment."""
    # TODO: overhaul with new data model
    print('Sending email.')
    if not tenant:
        user = anvil.users.get_user(allow_remembered=True)
        tenant = {'name': user['tenant']['name'], 'email': user['tenant']['email']}

    msg_body = f"""
    <p>Hi {user_ref['first_name']}!</p>

    <p>You are getting this message because either your membership payment has expired or
    your payments are not linked to your profile on our NotAlone platform.</p>

    <p>Please sign in to your account with this email: <b>{user_ref['email']}</b></p>

    <p>Sign in here: {anvil.server.get_app_origin()}</p>

    <h2>First Time Logging In?</h2>
    <p>If your email is not a gmail account, reset your password.</p>
    <p>If it is your first time and you do have a gmail account, log in with Google.</p>

    <p>Regards,</p>
    <p>{tenant['name']}</p>
    <p>Reply to: {tenant['email']}</p>
    """
    anvil.email.send(
        to=user_ref['email'],
        from_address='noreply',
        bcc=tenant['email'],
        from_name="NotAlone",
        subject="Membership Payment",
        html=msg_body
    )
