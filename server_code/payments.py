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
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        "plan_id": plan_id,
        "start_time": "2018-11-01T00:00:00Z",
        "quantity": "20",
        "shipping_amount": { 
            "currency_code": "USD",
            "value": "10.00"
        },
        "subscriber": {
            "name": {
                "given_name": "John",
                "surname": "Doe" 
            },
            "email_address": "customer@example.com",
            "shipping_address": {
                "name": { "full_name": "John Doe" },
                "address": {
                    "address_line_1": "2211 N First Street",
                    "address_line_2": "Building 17",
                    "admin_area_2": "San Jose",
                    "admin_area_1": "CA",
                    "postal_code": "95131",
                    "country_code": "US" 
                }
            }
        },
        "application_context": {
            "brand_name": "walmart",
            "locale": "en-US",
            "shipping_preference": "SET_PROVIDED_ADDRESS",
            "user_action": "SUBSCRIBE_NOW",
            "payment_method": {
                "payer_selected": "PAYPAL",
                "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
            },
            "return_url": "https://example.com/returnUrl",
            "cancel_url": "https://example.com/cancelUrl" 
        }
    }
    
    response = requests.post('https://api.paypal.com/v1/billing/subscriptions', headers=headers, json=data)
