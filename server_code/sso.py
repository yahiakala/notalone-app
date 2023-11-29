import anvil.server
import anvil.users
import anvil.secrets
from anvil.tables import app_tables

import base64
import hmac
import hashlib
import urllib.parse


@anvil.server.http_endpoint('/login-sso', cross_site_session=True)
def login_sso(sso, sig):
    # params['key']

    secret_key = anvil.secrets.get_secret('discourse_secret')

    # Verify the signature
    expected_sig = hmac.new(secret_key.encode(), msg=sso.encode(), digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, sig):
        raise anvil.server.HttpError(403, "Signature mismatch")

    # Decode the payload
    payload = base64.b64decode(urllib.parse.unquote(sso)).decode()
    params = dict(urllib.parse.parse_qsl(payload))
    nonce = params['nonce']

    user = anvil.users.get_user(allow_remembered=True)
    if not user or user['auth_forumchat'] != True:
        return "User not logged in or does not have access to forum."

    discourse_url = app_tables.forum.get(tenant=user['tenant'])['discourse_url']
    
    # Prepare the return payload with user info
    user_info = {
        'nonce': nonce,
        'email': user['email'],
        'external_id': user.get_id(),
        'username': user['first_name'] + '_' + user['last_name'],
        'name': user['first_name'] + ' ' + user['last_name']
    }
    return_payload = '&'.join([f"{key}={urllib.parse.quote_plus(str(value))}" for key, value in user_info.items()])

    # Sign the return payload
    return_sig = hmac.new(secret_key.encode(), msg=return_payload.encode(), digestmod=hashlib.sha256).hexdigest()

    # Base64-encode and URL-encode the return payload
    b64_return_payload = base64.b64encode(return_payload.encode()).decode()
    url_encoded_payload = urllib.parse.quote_plus(b64_return_payload)

    # Redirect back to Discourse
    discourse_redirect_url = f"https://{discourse_url}/session/sso_login?sso={url_encoded_payload}&sig={return_sig}"
    return anvil.server.HttpResponse(302, headers={"Location": discourse_redirect_url})