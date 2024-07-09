import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q

from anvil_squared.helpers import print_timestamp
from .helpers import validate_user, get_usermap, get_permissions, get_user_roles, usermap_row_to_dict, verify_tenant, populate_roles


# --------------------
# Non tenanted globals
# --------------------
@anvil.server.callable()
def get_tenant(user=None):
    """Get the tenant in this instance."""
    tenant = app_tables.tenants.get()

    if not tenant:
        return None
    # TODO: get more data if admin on these tenants.
    tenant_list = [
        {
            'tenant_id': tenant.get_id(),
            'name': tenant['name'],
            'discordlink': tenant['discord_invite'],
            'discourselink': tenant['discourse_url'],
            'waiver': tenant['waiver']
        }
    ]
    return tenant_list

# ----------------
# Tenanted globals
# ----------------
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    print_timestamp(f'get_tenanted_data: {key}')
    user = anvil.users.get_user(allow_remembered=True)
    # todo: verify tenant here?
    
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
    elif key == 'my_usermap':
        return get_my_usermap(tenant_id, user)


def get_my_usermap(tenant_id, user):
    tenant = verify_tenant(tenant_id, user)
    user_usermap = app_tables.usermap.client_writable(tenant=tenant, user=user).get()
    return user_usermap


def get_users_iterable(tenant_id, user):
    """Get an iterable of the users."""
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []
    return app_tables.usermap.client_readable(q.only_cols('user', 'notes'), tenant=tenant)


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