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
def get_tenants():
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        return app_tables.tenants.client_readable(q.only_cols('name'))
    else:
        return []


@anvil.server.callable(require_user=True)
def join_tenant(id):
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        user['tenant'] = app_tables.tenants.get_by_id(id)
        # Now let the user book an interview
        user['auth_booking'] = True
    return user


@anvil.server.callable(require_user=True)
def leave_tenant():
    user = anvil.users.get_user(allow_remembered=True)
    for key, val in user.items():
        if 'auth_' in key and 'auth_dev' not in key:
            user[key] = False
    user['tenant'] = None
    return user


@anvil.server.callable(require_user=True)
def update_user(user_dict):
    user = anvil.users.get_user(allow_remembered=True)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'consent_check', 'paypal_sub_id']:
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
def get_applicants():
    """Get restricted, client readable view of applicants."""
    clean_up_users()
    user = anvil.users.get_user(allow_remembered=True)
    readable_view = app_tables.users.client_readable(
        q.only_cols("email", "first_name", "last_name", "auth_profile", "auth_forumchat", "good_standing"),
        tenant=user['tenant']
    )
    # TODO: might not be necessary.
    # writable_view = app_tables.users.client_writable(
    #     q.only_cols('auth_profile', 'auth_forumchat'),
    #     tenant=user['tenant'],
    #     auth_forumchat=q.not_(True)
    # )
    return readable_view


@permission_required('auth_screenings')
def reassign_roles(user_dict, role_dict):
    """Reset roles for a user."""
    # TODO: refactor with a client writable view?
    user = anvil.users.get_user(allow_remembered=True)
    user_ref = app_tables.users.get(email=user_dict['email'], tenant=user['tenant'])
    for col_name, val in role_dict.items():
        if col_name in ['auth_profile', 'auth_forumchat']:
            user_ref[col_name] = val
    return user_ref


@permission_required('auth_booking')
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