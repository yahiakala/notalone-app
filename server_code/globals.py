import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

from anvil_squared.helpers import print_timestamp
from .helpers import verify_tenant


@anvil.server.callable(require_user=True)
def get_tenants():
    """Get a list of tenants for joining purposes."""
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        return app_tables.tenants.client_readable(q.only_cols('name'))
    else:
        return []

@anvil.server.callable(require_user=True)
def get_users(tenant_id):
    """Get a full list of the users."""
    print_timestamp('get_users')
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    if 'see_members' in permissions:
        return _get_users(user, tenant)
    else:
        return []


def _get_users(tenant, user, permissions):
    print_timestamp('_get_users: start')
    member_rows = app_tables.usermap.search(tenant=tenant)
    memberlist = [
        {
            'first_name': member['user']['first_name'] or '',
            'last_name': member['user']['last_name'] or '',
            'email': member['user']['email'],
            'fb_url': member['user']['fb_url'] or '',
            'discord': member['user']['discord'] or '',
            'fee': member['user']['fee'],
            'payment_status': member['user']['payment_status'],
            'payment_expiry': member['user']['payment_expiry'],
            'good_standing': member['user']['good_standing'],
            'last_login': member['user']['last_login'],
            'signed_up': member['user']['signed_up'],
            'paypal_sub_id': member['user']['paypal_sub_id'],
            'permissions': _get_permissions(member['user'], tenant.get_id())
        }
        for member in member_rows
    ]
    print_timestamp('_get_users: end')
    return memberlist


@anvil.server.callable(require_user=True)
def get_applicants(tenant_id):
    """Get applicants."""
    # TODO: break this up into two funcs
    print_timestamp('get_applicants')
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    if 'see_applicants' in permissions:
        return _get_applicants(user, tenant)


def _get_applicants(user, tenant, users=None):
    # TODO: change up query to not use auth flags
    app_q = app_tables.users.search(
        q.fetch_only("email", "first_name", "last_name", "auth_profile",
                    "auth_forumchat", "auth_booking", "good_standing", "signed_up"),
        tenant=tenant,
        auth_forumchat=q.not_(True),
        auth_profile=q.not_(True),
        auth_booking=True
    )
    print_timestamp('get_applicants done query')
    app_list = [
        {
            'email': i['email'],
            'first_name': i['first_name'] or '',
            'last_name': i['last_name'] or '',
            'auth_profile': i['auth_profile'],
            'auth_forumchat': i['auth_forumchat'],
            'auth_booking': i['auth_booking'],
            'good_standing': i['good_standing'],
            'signed_up': i['signed_up']
        }
        for i in app_q
    ]
    return app_list



@anvil.server.callable(require_user=True)
def get_screener_link(tenant_id):
    """Get random screener."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    if 'book_interview' in permissions:
        return _get_screener_link(user, tenant)


def _get_screener_link(user, tenant):
    import random
    records = [
        {
            'first_name': r['first_name'],
            'booking_link': r['booking_link'],
        }
        for r in app_tables.users.search(booking_link=q.not_(None),
                                        tenant=tenant,
                                        auth_screenings=True)
    ]
    # Shuffle the records list
    random.shuffle(records)
    return random.choice(records)


@anvil.server.callable(require_user=True)
def get_finances(tenant_id):
    """Get financial info."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    if 'see_finances' in permissions:
        return _get_finances(tenant)


def _get_finances(tenant):
    data = app_tables.finances.get(tenant=tenant)
    return {
        'rev_12': data['rev_12'] or 0,
        'budgets': data['budgets'] or {},
        'rev_12_active': data['rev_12_active'] or 0
    }


@anvil.server.callable(require_user=True)
def get_forumlink(tenant_id):
    """Get financial info."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    return _get_forumlink(tenant, permissions)


def _get_forumlink(tenant, permissions):
    if 'see_forum' in permissions:
        return 'https://' + app_tables.forum.get(tenant=tenant)['discourse_url']
    else:
        return ''


@anvil.server.callable(require_user=True)
def get_discordlink(tenant_id):
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    return _get_discordlink(tenant, permissions)


def _get_discordlink(tenant, permissions):
    if 'see_forum' in permissions:
        return app_tables.forum.get(tenant=tenant)['discord_invite']
    return ''


@anvil.server.callable(require_user=True)
def get_roles(tenant_id):
    """Get volunteer roles."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    return _get_roles(tenant, permissions)


def _get_roles(tenant, permissions):
    if 'see_forum' in permissions:
        return app_tables.roles.search(tenant=tenant)
    return []


@anvil.server.callable(require_user=True)
def get_roles_to_members(tenant_id):
    """Get a dict that maps volunteer roles to users."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    return _get_roles_to_members(tenant, permissions)


def _get_roles_to_members(tenant, permissions):
    if 'see_members' in permissions:
        role_members = []
        # users = list(app_tables.users.search(tenant=tenant))
        for role in app_tables.roles.search(tenant=tenant):
            role_members.append(
                {
                    'name': role['name'],
                    'last_update': role['last_update'],
                    'reports_to': role['reports_to'],
                    'member': [i for i in app_tables.users.search(tenant=tenant, roles=[role])]
                    # 'users': users
                }
            )
        return role_members
    return []


# @anvil.server.callable(require_user=True)
# def get_super_load():
#     user = anvil.users.get_user(allow_remembered=True)
#     data = {'users': [], 'applicants': []}
#     if user['auth_members']:
#         data['users'] = get_users()
#     if user['auth_screenings'] or user['auth_members']:
#         data['applicants'] = get_applicants()
#     return data


@anvil.server.callable(require_user=True)
def get_user_data(tenant_id):
    print_timestamp('get_user_data')
    user = anvil.users.get_user(allow_remembered=True)
    # Not gonna run the usermap, permissions, verify_tenant here due to speed
    return anvil.server.launch_background_task('get_user_data_bk', user, tenant_id)


@anvil.server.background_task
def get_user_data_bk(user, tenant_id):
    print_timestamp('get_user_data_bk: start')
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    data = {'users': [], 'applicants': []}
    data['permissions'] = permissions
    anvil.server.task_state['permissions'] = data['permissions']
    # Launch a separate bk task for these heavier ones?
    if 'see_members' in permissions:
        data['users'] = _get_users(user)
    anvil.server.task_state['users'] = data['users']
    if 'see_applicants' in permissions:
        data['applicants'] = _get_applicants(user)
    anvil.server.task_state['applicants'] = data['applicants']
    print_timestamp('get_user_data_bk: end')
    return data


# def get_usermap():
#     user = anvil.users.get_user(allow_remembered=True)
#     if not user:
#         raise ValueError('User is not logged in.')
#     return _get_usermap(user)


def _get_usermap(user):
    if not app_tables.usermap.get(user=user):
        # TODO: add some defaults
        usermap = app_tables.usermap.add_row(user=user)
    else:
        usermap = app_tables.usermap.get(user=user)
    return usermap


@anvil.server.callable(require_user=True)
def get_permissions(tenant_id):
    """Get the permissions of a user in a particular tenant."""
    user = anvil.users.get_user(allow_remembered=True)
    return _get_permissions(user, tenant_id)


def _get_permissions(user, tenant_id, usermap=None):
    """Get the permissions of a user in a particular tenant."""
    usermap = usermap or app_tables.usermap.get(user=user)
    try:
        user_permissions = set(
            permission["name"]
            for role in usermap["roles"]
            for permission in role["permissions"]
            if role['tenant'].get_id() == tenant_id
        )
        return list(user_permissions)
    except TypeError:
        return []