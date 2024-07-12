from anvil.tables import app_tables
import anvil.tables.query as q
# from anvil_squared.helpers import print_timestamp
import anvil.secrets


role_dict = {
    'Applicant': ['book_interview'],
    'Approved': ['see_profile'],
    'Member': ['see_profile', 'see_forum'],
    'Interviewer': ['see_profile', 'see_forum', 'see_applicants', 'see_members'],
    'Admin': ['see_profile', 'see_forum', 'see_applicants', 'see_members', 'edit_members', 'delete_members', 'delete_admin', 'edit_roles'],
}

perm_list = []
for key, val in role_dict.items():
    perm_list = perm_list + val

perm_list = list(set(perm_list))


def print_timestamp(input_str):
    import datetime as dt
    import pytz
    eastern_tz = pytz.timezone('US/Eastern')
    current_time = dt.datetime.now(eastern_tz)
    formatted_time = current_time.strftime('%H:%M:%S.%f')
    print(f"{input_str} : {formatted_time}")


def verify_tenant(tenant_id, user, tenant=None, usermap=None):
    """Verify a user is in this tenant."""
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    usermap = usermap or app_tables.usermap.get(user=user, tenant=tenant)

    if usermap['tenant'] == tenant:
        return tenant

    raise Exception('User does not belong to this tenant.')


def get_usermap(tenant_id, user, tenant=None):
    """Get a usermap. A user with no tenant will be added to this tenant."""
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    
    if not app_tables.usermap.get(user=user, tenant=tenant):
        new_roles = get_new_user_roles(None, tenant)
        usermap = app_tables.usermap.add_row(user=user, tenant=tenant, roles=new_roles)
    else:
        usermap = app_tables.usermap.get(user=user, tenant=tenant)
    return usermap


def get_new_user_roles(tenant_id, tenant=None):
    """Assign a brand new user a role in this tenant."""
    # This is where the logic of different tenants comes in.
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    new_roles = app_tables.roles.search(tenant=tenant, name='Applicant', can_edit=False)
    return list(new_roles)


def get_user_roles(tenant_id, user, usermap=None, tenant=None):
    """Get names of roles for a user in a tenant."""
    usermap = usermap if usermap is not None else app_tables.usermap.get(user=user)
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usermap=usermap)

    roles = []
    if usermap['roles']:
        for role in usermap['roles']:
            roles.append(role['name'])
    return list(set(roles))


def get_permissions(tenant_id, user, tenant=None, usermap=None):
    """Get the permissions of a user in a particular tenant."""
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usermap=usermap)
    usermap = usermap if usermap is not None else app_tables.usermap.get(user=user, tenant=tenant)
        
    user_permissions = []
    if usermap['roles']:
        for role in usermap['roles']:
            if role['permissions']:
                for permission in role['permissions']:
                    user_permissions.append(permission['name'])

    return list(set(user_permissions))


def validate_user(tenant_id, user, usermap=None, permissions=None, tenant=None):
    usermap = usermap if usermap is not None else get_usermap(tenant_id, user, tenant=tenant)
    tenant = tenant if tenant is not None else verify_tenant(tenant_id, user, usermap=usermap)
    permissions = permissions if permissions is not None else get_permissions(tenant_id, user, usermap=usermap, tenant=tenant)
    return tenant, usermap, permissions


def get_users_with_permission(tenant_id, permission, tenant=None):
    tenant = tenant or app_tables.tenants.get_by_id(tenant_id)
    perm_row = app_tables.permissions.get(name=permission)
    role_rows = app_tables.roles.search(permissions=perm_row, tenant=tenant)
    usermaps = app_tables.usermap.search(roles=q.any_of(*role_rows), tenant=tenant)
    return usermaps


def upsert_role(usermap, role_name):
    role = app_tables.roles.get(tenant=usermap['tenant'], name=role_name)
    if not usermap['roles']:
        usermap['roles'] = [role]
    elif role not in usermap['roles']:
        usermap['roles'] = usermap['roles'] + [role]


def usermap_row_to_dict(row):
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
        'permissions': get_permissions(None, row['user'], row['tenant'], row),
        'roles': get_user_roles(None, None, row, row['tenant']),
        'notes': row['notes']
    }
    return row_dict


def populate_permissions():
    """Populate the permissions table."""
    print_timestamp('populate_permissions')
    if len(app_tables.permissions.search()) == 0:
        for perm in perm_list:
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
    return app_tables.roles.search(tenant=tenant)


def decrypt(something):
    if something:
        return anvil.secrets.decrypt_with_key("encryption_key", something)
    else:
        return ''