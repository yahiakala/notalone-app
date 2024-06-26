import anvil.server
from anvil.tables import app_tables
from functools import wraps, partial


def print_timestamp(input_str):
    import datetime as dt
    import pytz
    eastern_tz = pytz.timezone('US/Eastern')
    current_time = dt.datetime.now(eastern_tz)
    formatted_time = current_time.strftime('%H:%M:%S.%f')
    print(f"{input_str} : {formatted_time}")


def permission_required(permissions):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return anvil.server.callable(require_user=partial(check_user_auth, permissions=permissions))(wrapper)
    return decorator


def check_user_auth(user, permissions):
    print('Checking user auth: ', permissions)
    if user is None:
        return False
        
    if isinstance(permissions, str):
        required_permissions = set([permissions])
    else:
        required_permissions = set(permissions)

    try:
        user_permissions = set(
            [
                permission
                for permission in required_permissions
                if user[permission] == True
            ]
        )
    except Exception:
        return False

    # ALL permissions option
    # if not required_permissions.issubset(user_permissions):
    #     return False

    # ANY permissions option
    if not len(user_permissions) > 0:
        return False
        
    return True



def verify_tenant(tenant_id, user, usermap=None):
    """Verify a user is in this tenant."""
    tenant_row = app_tables.tenants.get_by_id(tenant_id)
    usermap = usermap or app_tables.usermap.get(user=user)
    # TODO: might cause an error if none or just 1 tenant
    if tenant_row not in usermap['tenant']:
        raise Exception('User does not belong to this tenant.')
    return tenant_row


def get_usermap(user):
    if not app_tables.usermap.get(user=user):
        # TODO: add some defaults
        usermap = app_tables.usermap.add_row(user=user)
    else:
        usermap = app_tables.usermap.get(user=user)
    return usermap


def get_permissions(tenant_id, user, usermap=None, tenant=None):
    """Get the permissions of a user in a particular tenant."""
    usermap = usermap if usermap is not None else app_tables.usermap.get(user=user)
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usermap)
    try:
        user_permissions = set(
            permission["name"]
            for role in usermap["roles"]
            for permission in role["permissions"]
            if role['tenant'] == tenant
        )
        return list(user_permissions)
    except TypeError:
        return []


def validate_user(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap = usermap if usermap is not None else get_usermap(user)
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usermap)
    permissions = permissions if permissions is not None else get_permissions(tenant_id, user, usermap, tenant)
    return usermap, permissions, tenant


def populate_permissions():
    """Populate the permissions table."""
    permissions = [
        'see_applicants',
        'see_members',
        'edit_members',
        'delete_members',
        'see_profile',
        'see_forum',
        'book_interview',
        'see_finances',
        'dev',
        'edit_roles'
    ]
    if len(app_tables.permissions.search()) == 0:
        for perm in permissions:
            app_tables.permissions.add_row(name=perm)

def populate_roles():
    """Some basic roles."""
    pass