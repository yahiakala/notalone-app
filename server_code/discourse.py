import anvil.server
import anvil.users
import anvil.secrets
from anvil.tables import app_tables
import anvil.tables.query as q

import base64
import hmac
import hashlib
import urllib.parse
import json
from .helpers import validate_user


@anvil.server.http_endpoint('/discourse-sso', cross_site_session=True, enable_cors=True)
def login_sso(sso, sig, session_id=None):
    # Decode the payload
    payload = base64.b64decode(urllib.parse.unquote(sso)).decode()
    print(payload)
    params = dict(urllib.parse.parse_qsl(payload))
    print(params)
    nonce = params['nonce']

    user = anvil.users.get_user(allow_remembered=True)
    if not user:
        return anvil.server.HttpResponse(302, headers={"Location": anvil.server.get_app_origin()})

    discourse_url = params.get('discourse_domain')
    # return_sso_url
    discourse_url = params['return_sso_url'].replace('https://', '').replace('/session/sso_login', '')
    tenant = app_tables.tenants.get(discourse_url=q.ilike('%'+discourse_url+'%'))
    
    _, usermap, permissions = validate_user(None, user, tenant=tenant)
    
    if 'see_forum' not in permissions:
        return anvil.server.HttpResponse(302, headers={"Location": anvil.server.get_app_origin()})

    secret_key = anvil.secrets.get_secret('discourse_secret')

    expected_sig = hmac.new(secret_key.encode(), msg=sso.encode(), digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        raise anvil.server.HttpError(403, "Signature mismatch")

    # Prepare the return payload with user info
    first_name = user['first_name'] or ''
    last_name = user['last_name'] or ''
    if first_name == '' and last_name == '':
        username = user['email'].split('@')[0]
    else:
        username = first_name + ' ' + last_name
    
    user_info = {
        'nonce': nonce,
        'email': user['email'],
        'external_id': user.get_id(),
        'username': username,
        'name': username
    }
    print(user_info)
    return_payload = '&'.join([f"{key}={value}" for key, value in user_info.items()])

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
    discourse_redirect_url = f"https://{payload['return_sso_url']}?sso={url_encoded_payload}&sig={return_sig}"
    return anvil.server.HttpResponse(302, headers={"Location": discourse_redirect_url})


@anvil.server.http_endpoint('/new_member', methods=['POST'])
def new_member():
    """API endpoint for new member webhook."""
    payload = anvil.server.request.body.get_bytes()
    # print(payload)
    header_signature = anvil.server.request.headers.get('x-discourse-event-signature')
    # print(header_signature)
    # print(data)
    payload_dict = json.loads(payload.decode('utf-8'))
    print(payload_dict)

    # TODO: untested
    DISCOURSE_URL = anvil.server.request.headers.get('x-discourse-instance')
    
    # Verify the signature
    if not verify_signature(payload, header_signature, DISCOURSE_URL):
        # If the signature verification fails, return a 403 Forbidden response
        return anvil.server.HttpResponse(403, "Forbidden: Signature mismatch.")

    
    if payload_dict:
        new_member_username = payload_dict['user']['username']
        new_member_name = new_member_username.split('_')[0]
        welcome_message = f"Welcome to the forum, @{new_member_username}! We're glad to have you here. Please tell the group a bit about yourself!"
        title = f'[New Member] Welcome {new_member_name}!'
        create_topic(title=title, message=welcome_message, discourse_url=DISCOURSE_URL)
    return anvil.server.HttpResponse(200)


def create_topic(title='Test post', message='Test post this is a test', discourse_url=None):
    post_url = f"{discourse_url}/posts"
    api_key = app_tables.tenants.get(discourse_url=discourse_url)['discourse_api_key']
    headers = {
        'Api-Key': api_key,
        'Api-Username': 'system',
        'Content-Type': 'application/json'
    }
    post_data = {
        'title': title,
        'raw': message,
        'category': 4
    }
    try:
        response = anvil.http.request(post_url, method="POST", data=post_data, headers=headers, json=True)
    except anvil.http.HttpError as e:
        print(e.content)
        print(f"Error {e.status}")
    
    print(response)


def verify_signature(payload, header_signature, discourse_url):
    # Assuming Discourse sends the signature in the format `sha256=signature`
    algorithm, signature = header_signature.split('=')
    secret_key = anvil.secrets.get_secret('discourse_secret')
    # Use the corresponding hash function for the algorithm used by Discourse
    if algorithm == 'sha256':
        hash_function = hashlib.sha256
    else:
        # Handle other algorithms or raise an error
        raise ValueError("Unsupported algorithm")

    # Create a new HMAC object using the secret and the hash function
    hmac_object = hmac.new(secret_key.encode(), payload, hash_function)
    # Generate the HMAC signature
    generated_signature = hmac_object.hexdigest()

    # Securely compare the generated signature with the received signature
    return hmac.compare_digest(generated_signature, signature)