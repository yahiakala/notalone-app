import anvil.server
import anvil.secrets
import anvil.http
from anvil.tables import app_tables
import anvil.tables.query as q

from .tasks import role_pending_plus, role_leader
# https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions_create

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


def get_subscriptions(subscription_id):
    import datetime as dt
    
    if not subscription_id:
        return None, None
    import requests
    access_token = get_paypal_auth()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    subscription_detail_response = requests.get(f'https://api.paypal.com/v1/billing/subscriptions/{subscription_id}', headers=headers)
    try:
        status = subscription_detail_response.json()['status']
        last_payment = dt.datetime.fromisoformat(
            subscription_detail_response.json()['billing_info']['last_payment']['time'].replace("Z", "+00:00")
        ).date()
    except KeyError as e:
        status = None
        last_payment = None
    return status, last_payment


@anvil.server.callable(require_user=role_pending_plus)
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


@anvil.server.callable(require_user=role_leader)
def check_sub(user_dict):
    from dateutil.relativedelta import relativedelta
    import datetime as dt
    
    user_ref = app_tables.users.get(email=user_dict['email'])
    status, last_payment = get_subscriptions(user_ref['paypal_sub_id'])
    user_ref['payment_status'] = status
    if last_payment:
        user_ref['payment_expiry'] = last_payment + relativedelta(years=1)
    if user_ref['payment_expiry'] >= dt.date.today() or status == 'ACTIVE' or user_ref['fee'] == 0:
        user_ref['good_standing'] = True
    return user_ref

#%% Scheduled Task -------------------------------
@anvil.server.background_task
def check_subs():
    for user in app_tables.users.search(roles=['member']):
        _ = check_sub(user)



    