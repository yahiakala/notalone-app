import anvil.server
import anvil.users


@anvil.server.http_endpoint('/login-sso')
def login_sso(**params):
    # params['key']
    user = anvil.users.get_user(allow_remembered=True)
    if user:
        return user
    else:
        anvil.users.login_with_form(allow_remembered=True)