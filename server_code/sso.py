import anvil.server
import anvil.users


@anvil.server.http_endpoint('/login-sso', cross_site_session=True)
def login_sso(**params):
    # params['key']
    user = anvil.users.get_user(allow_remembered=True)
    if user:
        return "User logged in"
    else:
        return "user not logged in"