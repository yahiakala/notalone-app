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
        return "User not logged in or does not have access to forum."

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