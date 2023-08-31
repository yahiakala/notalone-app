import anvil.server
import anvil.secrets
import anvil.http
from anvil.tables import app_tables
import anvil.tables.query as q

from .tasks import role_pending_plus
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
    if not subscription_id:
        return False
    import requests
    access_token = get_paypal_auth()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    subscription_detail_response = requests.get(f'https://api.paypal.com/v1/billing/subscriptions/{subscription_id}', headers=headers)
    status = subscription_detail_response.json()['status']
    return status == 'ACTIVE'


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
    row['payment_enrolled'] = True
    return 'Payment success! You can close this tab.'


@anvil.server.http_endpoint('/cancel-sub')
def cancel_sub(**params):
    row = app_tables.users.get(paypal_sub_id=params['subscription_id'])
    row['paypal_sub_id'] = None
    return 'You have cancelled enrollment. You can close this tab.'

#%% Scheduled Task -------------------------------
@anvil.server.background_task
def check_subs():
    for user in app_tables.users.search(roles=['member']):
        if get_subscriptions(user['paypal_sub_id']):
            user['payment_enrolled'] = True
        else:
            user['payment_enrolled'] = False