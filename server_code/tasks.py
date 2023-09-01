import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q

from .helpers import role_check

from functools import partial

# def role_screener(user):
#     return 'screener' in user['roles'] or 'leader' in user['roles']


# def role_leader(user):
#     return 'leader' in user['roles']

# def role_pending_plus(user):
#     return 'pending' in user['roles'] or 'member' in user['roles']


def clean_up_user(user):
    if not user['roles']:
        user['roles'] = ['applied']
    if not user['first_name']:
        user['first_name'] = ''
    if not user['last_name']:
        user['last_name'] = ''
    return user


def clean_up_users():
    # for user in app_tables.users.search(roles=None):
    #     user['roles'] = ['applied']
    for user in app_tables.users.search(first_name=None):
        user['first_name'] = ''
    for user in app_tables.users.search(last_name=None):
        user['last_name'] = ''


@anvil.server.callable(require_user=True)
def update_user(user_dict):
    user = anvil.users.get_user(allow_remembered=True)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'payment_email', 'consent_check', 'paypal_sub_id']:
        if user[key] != user_dict[key]:
            user[key] = user_dict[key]
    user = clean_up_user(user)
    return user


@anvil.server.callable(require_user=partial(role_check, permissions=['members']))
def get_users():
    """Get a full list of the users."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.users.client_writable(tenant=user['tenant'])


@anvil.server.callable(require_user=partial(role_check, permissions=['screenings']))
def get_applied():
    """Get a full list of the users."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.users.search(roles=None, tenant=user['tenant'])


@anvil.server.callable(require_user=partial(role_check, permissions=['screenings']))
def get_pending():
    """Get a full list of the users."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.users.search(roles=['pending'], tenant=user['tenant'])


@anvil.server.callable(require_user=partial(role_check, permissions=['screenings']))
def reassign_roles(user_dict, roles):
    """Add pending status to applicant."""
    user = anvil.users.get_user(allow_remembered=True)
    user_ref = app_tables.users.get(email=user_dict['email'], tenant=user['tenant'])
    user_ref['roles'] = roles
    return user_ref


@anvil.server.callable(require_user=True)
def get_screener_link():
    """Get random screener."""
    import random
    user = anvil.users.get_user(allow_remembered=True)
    screener_roles = app_tables.roles.search(screenings=True)
    return random.choice(
        [
            {
                'first_name': r['first_name'],
                'booking_link': r['booking_link'],
            }
            for r in app_tables.users.search(booking_link=q.not_(None), tenant=user['tenant'])
            if any(role in r['roles'] for role in screener_roles)
        ]
    )