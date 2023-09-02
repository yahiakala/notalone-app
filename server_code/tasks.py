import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q

from .helpers import permission_required


def clean_up_user(user):
    if not user['first_name']:
        user['first_name'] = ''
    if not user['last_name']:
        user['last_name'] = ''
    return user


def clean_up_users():
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


@permission_required('auth_members')
def get_users():
    """Get a full list of the users."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.users.client_writable(tenant=user['tenant'])


@permission_required('auth_screenings')
def get_applied():
    """Get users that have applied but not screened yet."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.users.search(auth_profile=False, tenant=user['tenant'])


@permission_required('auth_screenings')
def get_pending():
    """Get users that have been screened and approved."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.users.search(auth_profile=True, auth_forumchat=False, tenant=user['tenant'])


@permission_required('auth_screenings')
def reassign_roles(user_dict, roles):
    """Reset roles for a user."""
    user = anvil.users.get_user(allow_remembered=True)
    user_ref = app_tables.users.get(email=user_dict['email'], tenant=user['tenant'])
    for role, val in roles.items():
        user_ref[role] = val
    return user_ref


@anvil.server.callable(require_user=True)
def get_screener_link():
    """Get random screener."""
    import random
    user = anvil.users.get_user(allow_remembered=True)
    return random.choice(
        [
            {
                'first_name': r['first_name'],
                'booking_link': r['booking_link'],
            }
            for r in app_tables.users.search(booking_link=q.not_(None),
                                             tenant=user['tenant'],
                                             auth_screenings=True)
        ]
    )