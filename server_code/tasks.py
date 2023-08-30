import anvil.server
import anvil.users

@anvil.server.callable(require_user=True)
def update_user(user_dict):
    user = anvil.users.get_user(allow_remembered=True)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'payment_email', 'consent_check']:
        if user[key] != user_dict[key]:
            user[key] = user_dict[key]
    return user