import anvil.server
import anvil.secrets


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
    import requests
    access_token = get_paypal_auth()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    subscription_detail_response = requests.get(f'https://api.paypal.com/v1/billing/subscriptions/{subscription_id}', headers=headers)
    status = subscription_detail_response.json()['status']
    return status == 'ACTIVE'


def create_sub(plan_id):
    import requests
    access_token = get_paypal_auth()

    response = anvil.http.request(
        'https://api.paypal.com/v1/billing/subscriptions',
        method='POST',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        },
        json={
            'plan_id': plan_id,
            'application_context': {
                'return_url': 'https://your-return-url',
                'cancel_url': 'https://your-cancel-url',
            },
        },
    )
    return response['id'], response['links'][0]['href']
    
