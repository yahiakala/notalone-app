import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

from anvil_squared.helpers import print_timestamp
from .helpers import validate_user, get_usermap

# from anvil_extras import authorisation
# from anvil_extras.authorisation import authorisation_required

# authorisation.set_config({'get_roles': 'usermap'})


# --------------------
# Non tenanted globals
# --------------------
@anvil.server.callable(require_user=True)
def get_tenants():
    """Get a list of tenants for joining purposes."""
    # This being slow is okay.
    user = anvil.users.get_user(allow_remembered=True)
    usermap = get_usermap(user)
    if usermap['tenant'] is None:
        return app_tables.tenants.client_readable(q.only_cols('name'))
    else:
        return []


# ----------------
# Tenanted globals
# ----------------
# @anvil.server.callable(require_user=True)
# def get_tenanted_data(tenant_id, key):
#     # TODO: deprecate as only want to get tenanted globals from a bk task.
#     print_timestamp(f'get_tenanted_data: {key}')
#     user = anvil.users.get_user(allow_remembered=True)
    
#     if key == 'users':
#         return get_users(tenant_id, user)
#     elif key == 'applicants':
#         return get_applicants(tenant_id, user)
#     elif key == 'screenerlink':
#         return get_screenerlink(tenant_id, user)
#     elif key == 'forumlink':
#         return get_discordlink(tenant_id, user)
#     elif key == 'discordlink':
#         return get_forumlink(tenant_id, user)
#     elif key == 'roles':
#         return get_roles(tenant_id, user)
#     elif key == 'roles_to_members':
#         return get_roles_to_members(tenant_id, user)


def get_users(tenant_id, user, usermap=None, permissions=None, tenant=None):
    print_timestamp('_get_users: start')
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
    
    if 'see_members' not in permissions:
        return []
    
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


def get_applicants(tenant_id, user, usermap=None, permissions=None, tenant=None, users=None):
    # TODO: change up query to not use auth flags
    # TODO: use users if defined
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
    
    if 'see_applicants' not in permissions:
        return []
    
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


def get_screenerlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    import random

    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)

    if 'book_interview' not in permissions:
        return ''

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


def get_finances(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)

    if 'see_finances' not in permissions:
        return {}
    
    data = app_tables.finances.get(tenant=tenant)
    return {
        'rev_12': data['rev_12'] or 0,
        'budgets': data['budgets'] or {},
        'rev_12_active': data['rev_12_active'] or 0
    }


def get_forumlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
    if 'see_forum' in permissions:
        return 'https://' + app_tables.forum.get(tenant=tenant)['discourse_url']
    else:
        return ''


def get_discordlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
    if 'see_forum' in permissions:
        return app_tables.forum.get(tenant=tenant)['discord_invite']
    return ''


def get_roles(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
    if 'see_forum' in permissions:
        return app_tables.roles.search(tenant=tenant)
    return []


def get_roles_to_members(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
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


# ------------------------------------------------------
# Getting all the tenanted globals in a background task.
# ------------------------------------------------------
@anvil.server.callable(require_user=True)
def get_user_data(tenant_id):
    print_timestamp('get_user_data')
    user = anvil.users.get_user(allow_remembered=True)
    # Not gonna run the usermap, permissions, verify_tenant here due to speed
    return anvil.server.launch_background_task('get_user_data_bk', tenant_id, user)


@anvil.server.background_task
def get_user_data_bk(tenant_id, user, usermap=None, permissions=None, tenant=None):
    print_timestamp('get_user_data_bk: start')
    usermap, permissions, tenant = validate_user(tenant_id, user, usermap, permissions, tenant)
    # In future, might launch separate bk tasks for each thing.
    
    data = {}
    data['permissions'] = permissions
    anvil.server.task_state['permissions'] = data['permissions']

    data['forumlink'] = get_forumlink(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['forumlink'] = data['forumlink']
    
    data['screenerlink'] = get_screenerlink(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['screenerlink'] = data['screenerlink']

    data['applicants'] = get_applicants(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['applicants'] = data['applicants']

    data['users'] = get_users(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['users'] = data['users']

    data['discordlink'] = get_discordlink(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['discordlink'] = data['discordlink']

    data['roles'] = get_roles(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['roles'] = data['roles']
    
    data['roles_to_members'] = get_roles_to_members(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['roles_to_members'] = data['roles_to_members']
        
    print_timestamp('get_user_data_bk: end')
    return data
