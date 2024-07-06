import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

from anvil_squared.helpers import print_timestamp
from .helpers import validate_user, get_usermap, get_permissions, get_user_roles


# --------------------
# Non tenanted globals
# --------------------
@anvil.server.callable(require_user=True)
def get_data(name):
    user = anvil.users.get_user(allow_remembered=True)
    if name == 'tenants':
        return get_tenants(user)
    elif name == 'my_tenants':
        return get_my_tenants(user)


def get_tenants(user):
    """Get a list of tenants for joining purposes."""
    # This being slow is okay.
    # user = anvil.users.get_user(allow_remembered=True)
    return app_tables.tenants.client_readable(q.only_cols('name'))


def get_my_tenants(user):
    """Get a list of tenants for joining purposes."""
    # This being slow is okay.
    usermaps = app_tables.usermap.search(user=user)

    # TODO: get more data if admin on these tenants.
    tenant_list = [
        {
            'tenant_id': i['tenant'].get_id(),
            'name': i['tenant']['name'],
            'discordlink': i['tenant']['discord_invite'],
            'discourselink': i['tenant']['discourse_url'],
            'waiver': i['tenant']['waiver']
        }
        for i in usermaps
    ]
    return tenant_list


# ----------------
# Tenanted globals
# ----------------
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    # TODO: deprecate as only want to get tenanted globals from a bk task.
    print_timestamp(f'get_tenanted_data: {key}')
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.session['tenant_id'] = tenant_id
    
    if key == 'users':
        return get_users_iterable(tenant_id, user)
    elif key == 'permissions':
        return get_permissions(tenant_id, user)
    elif key == 'screenerlink':
        return get_screenerlink(tenant_id, user)
    elif key == 'forumlink':
        return get_discordlink(tenant_id, user)
    elif key == 'discordlink':
        return get_forumlink(tenant_id, user)
    elif key == 'roles':
        return get_roles(tenant_id, user)


def get_users_iterable(tenant_id, user):
    """Get an iterable of the users."""
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []
    return app_tables.usermap.client_readable(q.only_cols('user'), tenant=tenant)


def get_users(tenant_id, user, usermap=None, permissions=None, tenant=None):
    print_timestamp('_get_users: start')
    tenant, usermap, permissions = validate_user(tenant_id, user, usermap=usermap, permissions=permissions, tenant=tenant)
    
    if 'see_members' not in permissions:
        return []

    member_rows = app_tables.usermap.search(tenant=tenant)
    if anvil.server.context.background_task_id:
        anvil.server.task_state['users_len'] = len(member_rows)

    memberlist = []
    for member in member_rows:
        try:
            memberlist.append(usermap_row_to_dict(tenant, member))
        except anvil.tables.RowDeleted:
            member.delete()
            if anvil.server.context.background_task_id:
                anvil.server.task_state['users_len'] = anvil.server.task_state['users_len'] - 1

        if anvil.server.context.background_task_id:
            anvil.server.task_state['users'] = memberlist

    print_timestamp('_get_users: end')
    return memberlist


def usermap_row_to_dict(tenant, row):
    row_dict = {
        'first_name': row['user']['first_name'] or '',
        'last_name': row['user']['last_name'] or '',
        'email': row['user']['email'],
        'discord': row['discord'] or '',
        'fee': row['fee'],
        'phone': row['phone'] or '',
        'consent_check': row['consent_check'],
        'booking_link': row['booking_link'],
        'payment_status': row['payment_status'],
        'payment_expiry': row['payment_expiry'],
        'last_login': row['user']['last_login'],
        'signed_up': row['user']['signed_up'],
        'paypal_sub_id': row['paypal_sub_id'],
        'permissions': get_permissions(None, row['user'], row, tenant),
        'roles': get_user_roles(None, None, row, tenant),
        'notes': row['notes']
    }
    return row_dict


def get_screenerlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    """Get a random interviewer name and link."""
    import random

    tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
    if 'book_interview' not in permissions:
        return ''

    # TODO: in future, make sure they have an interviewer role
    screeners = app_tables.users.search(
        booking_link=q.not_(None),
        tenant=tenant
    )
    
    records = [
        {
            'first_name': r['first_name'],
            'booking_link': r['booking_link'],
        }
        for r in screeners
    ]
    # Shuffle the records list
    random.shuffle(records)
    return random.choice(records)


def get_finances(tenant_id, user, usermap=None, permissions=None, tenant=None):
    """Get financial data from the tenant table."""
    tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)

    if 'see_finances' not in permissions:
        return {}
    
    data = app_tables.finances.get(tenant=tenant)
    return {
        'rev_12': data['rev_12'] or 0,
        'budgets': data['budgets'] or {},
        'rev_12_active': data['rev_12_active'] or 0
    }


def get_forumlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    """Get link to forum."""
    tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
    return tenant['discourse_url']


def get_discordlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
    if 'see_forum' in permissions:
        return tenant['discord_invite']
    return ''


def get_roles(tenant_id, user, usermap=None, permissions=None, tenant=None):
    tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
    if 'see_forum' in permissions:
        role_list = []
        role_search = app_tables.roles.search(tenant=tenant)
        if anvil.server.context.background_task_id:
            anvil.server.task_state['roles_len'] = len(role_search)
        for role in role_search:
            if role['permissions']:
                role_perm = [j['name'] for j in role['permissions']]
            else:
                role_perm = []
            role_list.append(
                {
                    'name': role['name'],
                    'reports_to': role['reports_to'],
                    'last_update': role['last_update'],
                    'guide': role['guide'],
                    'permissions': role_perm
                }
            )
            if anvil.server.context.background_task_id:
                anvil.server.task_state['roles'] = role_list
        return role_list
    return []


# ------------------------------------------------------
# Getting all the tenanted globals in a background task.
# ------------------------------------------------------
@anvil.server.callable(require_user=True)
def get_tenanted_data_call_bk(tenant_id):
    print_timestamp('get_tenanted_data_call_bk')
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.session['tenant_id'] = tenant_id
    return anvil.server.launch_background_task('get_tenanted_data_bk', tenant_id, user)


@anvil.server.background_task
def get_tenanted_data_bk(tenant_id, user, usermap=None, permissions=None, tenant=None):
    print_timestamp('get_tenanted_data_bk: start')
    tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
    # In future, might launch separate bk tasks for each thing.
    
    data = {}
    data['permissions'] = permissions
    anvil.server.task_state['permissions'] = data['permissions']

    data['forumlink'] = get_forumlink(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['forumlink'] = data['forumlink']
    
    data['screenerlink'] = get_screenerlink(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['screenerlink'] = data['screenerlink']

    data['users'] = get_users(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['users'] = data['users']

    # data['applicants'] = get_applicants(tenant_id, user, usermap, permissions, tenant, data['users'])
    # anvil.server.task_state['applicants'] = data['applicants']

    data['discordlink'] = get_discordlink(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['discordlink'] = data['discordlink']

    data['roles'] = get_roles(tenant_id, user, usermap, permissions, tenant)
    anvil.server.task_state['roles'] = data['roles']
    
    # data['roles_to_members'] = get_roles_to_members(tenant_id, user, usermap, permissions, tenant)
    # anvil.server.task_state['roles_to_members'] = data['roles_to_members']
        
    print_timestamp('get_tenanted_data_bk: end')
    return data
