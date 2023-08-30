import anvil.server
import anvil.users
from anvil.tables import app_tables

@anvil.server.callable(require_user=True)
def update_user(user_dict):
    user = anvil.users.get_user(allow_remembered=True)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'payment_email', 'consent_check']:
        if user[key] != user_dict[key]:
            user[key] = user_dict[key]
    return user

@anvil.server.callable(require_user=True)
def get_users():
    """Get a full list of the users."""
    user = anvil.users.get_user(allow_remembered=True)
    if 'leader' in user['roles']:
        return app_tables.users.client_writable()
    elif 'screener' in user['roles']:
        return app_tables.users.search(roles=None)
    else:
        return None