import anvil.server
import anvil.secrets
import anvil.http
from anvil.tables import app_tables
import anvil.tables.query as q

# https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions_create
from .helpers import permission_required


def get_paypal_auth():
    import requests
    client_id = anvil.secrets.get_secret('paypal_client_id')
    client_secret = anvil.secrets.get_secret('paypal_secret')
    
    auth_response = requests.post('https://api.paypal.com/v1/oauth2/token', 
                                auth=(client_id, client_secret), 
                                headers={'Accept': 'application/json', 'Accept-Language': 'en_US'}, 
                                data={'grant_type': 'client_credentials'})
    
    auth_response_json = auth_response.json()
    access_token = auth_response_json['access_token']
    return access_token


def get_subscriptions(subscription_id, verbose=False):
    import datetime as dt
    
    if not subscription_id:
        return None, None, None
    import requests
    access_token = get_paypal_auth()
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
    except KeyError as e:
        status = None
        last_payment = None
        payment_amt = None
    return status, last_payment, payment_amt


@anvil.server.callable(require_user=True)
def create_sub(plan_amt):
    import requests
    access_token = get_paypal_auth()
    print(anvil.server.get_app_origin())

    if plan_amt == 10:
        plan_id = anvil.secrets.get_secret('pp_plan_id_10')
    else:
        plan_id = anvil.secrets.get_secret('pp_plan_id_50')

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
                    'return_url': anvil.server.get_api_origin() + '/capture-sub',
                    'cancel_url': anvil.server.get_api_origin() + '/cancel-sub'
                }
            },
            json=True
        )
        return response['id'], response['links'][0]['href']
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")


@anvil.server.http_endpoint('/capture-sub')
def capture_sub(**params):
    row = app_tables.users.get(paypal_sub_id=params['subscription_id'])
    row['good_standing'] = True
    return 'Payment success! You can close this tab.'


@anvil.server.http_endpoint('/cancel-sub')
def cancel_sub(**params):
    row = app_tables.users.get(paypal_sub_id=params['subscription_id'])
    row['paypal_sub_id'] = None
    return 'You have cancelled enrollment. You can close this tab.'


@permission_required('auth_members')
def check_sub(user_dict):
    from dateutil.relativedelta import relativedelta
    import datetime as dt
    if user_dict:
        user_ref = app_tables.users.get(email=user_dict['email'])
    else:
        user = anvil.users.get_user(allow_remembered=True)
        user_ref = app_tables.users.get(email=user_dict['email'], tenant=user['tenant'])

    if not user_ref:
        return None

    # TODO: add payment amount to the col in the db
    status, last_payment, payment_amt = get_subscriptions(user_ref['paypal_sub_id'])
    user_ref['payment_status'] = status
    user_ref['fee'] = payment_amt
    if last_payment:
        user_ref['payment_expiry'] = last_payment + relativedelta(years=1)
        if user_ref['payment_expiry'] >= dt.date.today() or status == 'ACTIVE' or user_ref['fee'] == 0:
            user_ref['good_standing'] = True
            # Allow the user in the forum if they have not been banned/removed.
            if user_ref['auth_profile']:
                user_ref['auth_forumchat'] = True
        else:
            # Disable the user's forum privileges until back in good standing.
            user_ref['good_standing'] = False
            user_ref['auth_forumchat'] = False
    return user_ref
      

#%% Scheduled Task -------------------------------
@anvil.server.background_task
def check_subs():
    for user in app_tables.users.search():
        # TODO: break up check_sub to accept a user tenant
        _ = check_sub(user)


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


@permission_required('auth_members')
def notify_payment(user_ref):
    """Notify the member they need to make a payment."""
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
    <p>{user_ref['tenant']['name']}</p>
    """
    anvil.email.send(
        to=user_ref['email'],
        from_address=user_ref['tenant']['email'],
        from_name="NotAlone",
        subject="Membership Payment",
        html=msg_body
    )


@permission_required('auth_members')
def notify_all_payments():
    anvil.server.launch_background_task('check_expired_payments')


@anvil.server.background_task
def check_expired_payments():
    for user in app_tables.users.search(good_standing=False, auth_profile=True):
        notify_payment(user)