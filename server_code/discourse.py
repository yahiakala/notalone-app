import anvil.server
import anvil.users
import anvil.secrets
from anvil.tables import app_tables

import base64
import hmac
import hashlib
import urllib.parse


@anvil.server.http_endpoint('/login-sso', cross_site_session=True, enable_cors=True)
def login_sso(sso, sig, session_id=None):
    # params['key']
    # print(sso)
    # print(sig)

    secret_key = anvil.secrets.get_secret('discourse_secret')

    # Verify the signature
    expected_sig = hmac.new(secret_key.encode(), msg=sso.encode(), digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        raise anvil.server.HttpError(403, "Signature mismatch")

    # Decode the payload
    payload = base64.b64decode(urllib.parse.unquote(sso)).decode()
    params = dict(urllib.parse.parse_qsl(payload))
    nonce = params['nonce']

    user = None
    # if session_id:
    #     user = get_user_by_session_id(session_id)
    if not user:
        user = anvil.users.get_user(allow_remembered=True)
    print('user')
    print(user)
    if not user or user['auth_forumchat'] != True:
        return anvil.server.HttpResponse(302, headers={"Location": anvil.server.get_app_origin()})

    discourse_url = app_tables.forum.get(tenant=user['tenant'])['discourse_url']
    # print(discourse_url)
    
    # Prepare the return payload with user info
    user_info = {
        'nonce': nonce,
        'email': user['email'],
        'external_id': user.get_id(),
        'username': user['first_name'] + '_' + user['last_name'],
        'name': user['first_name'] + ' ' + user['last_name']
    }
    print(user_info)
    # unsigned payload generated
    # return_payload = '&'.join([f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in user_info.items()])
    return_payload = '&'.join([f"{key}={value}" for key, value in user_info.items()])
    # print(return_payload)

    # Base64-encode and URL-encode the return payload
    b64_return_payload = base64.b64encode(return_payload.encode()).decode()
    print('b64 return payload')
    # print(b64_return_payload)
    url_encoded_payload = urllib.parse.quote_plus(b64_return_payload)
    print('url encoded payload')
    # print(url_encoded_payload)

    # Sign the return payload
    return_sig = hmac.new(secret_key.encode(), msg=b64_return_payload.encode(), digestmod=hashlib.sha256).hexdigest()
    print('return sig')
    # print(return_sig)

    # Redirect back to Discourse
    discourse_redirect_url = f"https://{discourse_url}/session/sso_login?sso={url_encoded_payload}&sig={return_sig}"
    return anvil.server.HttpResponse(302, headers={"Location": discourse_redirect_url})


@anvil.server.http_endpoint('/new_member', methods=['POST'])
def new_member(**data):
    payload = anvil.server.request.body
    header_signature = anvil.server.request.headers.get('X-Hub-Signature', '')

    # Verify the signature
    if not verify_signature(payload, header_signature):
        # If the signature verification fails, return a 403 Forbidden response
        return anvil.server.HttpResponse(403, "Forbidden: Signature mismatch.")

    DISCOURSE_API_KEY = anvil.secrets.get_secret('discourse_api_key')
    DISCOURSE_API_USERNAME = 'system'
    DISCOURSE_URL = 'https://your.discourse.forum'
    new_member_username = data['user']['username']
    print(data)
    # new_member_username = data.get('user', {}).get('username', '')
    # if not new_member_username:
    #     return anvil.server.HttpResponse(400, "Bad Request: Missing new member username.")
    
    # # Construct the welcome message
    # welcome_message = f"Welcome to the forum, @{new_member_username}! We're glad to have you here. Please tell the group a bit about yourself!"
    
    # # Post the welcome message to Discourse
    # post_url = f"{DISCOURSE_URL}/posts"
    # headers = {
    #     'Api-Key': DISCOURSE_API_KEY,
    #     'Api-Username': DISCOURSE_API_USERNAME,
    #     'Content-Type': 'application/json'
    # }
    # post_data = {
    #     'title': f'[New Member] Welcome {new_member_username}!',
    #     'raw': welcome_message,
    #     'category': 4  # Specify the category ID where the post should be created
    # }
    # response = anvil.http.request(post_url, method="POST", data=post_data, headers=headers, json=True)
    
    # if response.status_code == 200:
    #     return anvil.server.HttpResponse(200, 'Welcome post created successfully')
    # else:
    #     # Log or handle error appropriately here
    #     return anvil.server.HttpResponse(500, 'Failed to create welcome post')
    return anvil.server.HttpResponse(200)


def verify_signature(payload, header_signature):
    # Assuming Discourse sends the signature in the format `sha256=signature`
    algorithm, signature = header_signature.split('=')
    # Use the corresponding hash function for the algorithm used by Discourse
    if algorithm == 'sha256':
        hash_function = hashlib.sha256
    else:
        # Handle other algorithms or raise an error
        raise ValueError("Unsupported algorithm")

    # Create a new HMAC object using the secret and the hash function
    hmac_object = hmac.new(WEBHOOK_SECRET.encode(), payload, hash_function)
    # Generate the HMAC signature
    generated_signature = hmac_object.hexdigest()

    # Securely compare the generated signature with the received signature
    return hmac.compare_digest(generated_signature, signature)