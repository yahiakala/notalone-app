from anvil.tables import app_tables
import anvil.tables.query as q
# from anvil_squared.helpers import print_timestamp


def print_timestamp(input_str):
    import datetime as dt
    import pytz
    eastern_tz = pytz.timezone('US/Eastern')
    current_time = dt.datetime.now(eastern_tz)
    formatted_time = current_time.strftime('%H:%M:%S.%f')
    print(f"{input_str} : {formatted_time}")


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

role_dict = {
        'Applicant': ['book_interview'],
        'Approved': ['see_profile'],
        'Member': ['see_profile', 'see_forum'],
        'Interviewer': ['see_profile', 'see_forum', 'see_applicants', 'see_members'],
        'Admin': ['see_profile', 'see_forum', 'see_applicants', 'see_members', 'edit_members', 'delete_members', 'delete_admin', 'edit_roles']
    }


def populate_permissions():
    """Populate the permissions table."""
    print_timestamp('populate_permissions')
    if len(app_tables.permissions.search()) == 0:
        for perm in permissions:
            app_tables.permissions.add_row(name=perm)


def populate_roles(tenant):
    """Some basic roles."""
    print_timestamp('populate_roles')
    
    for key, val in role_dict.items():
        perm_rows = app_tables.permissions.search(name=q.any_of(*val))
        if len(perm_rows) == 0:
            populate_permissions()
            perm_rows = app_tables.permissions.search(name=q.any_of(*val))
            
        is_it_there = app_tables.roles.get(name=key, tenant=tenant)
        if not is_it_there:
            app_tables.roles.add_row(name=key, tenant=tenant, permissions=list(perm_rows), can_edit=False)