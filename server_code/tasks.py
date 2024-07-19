import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.email
import anvil.secrets

from .helpers import print_timestamp, verify_tenant, validate_user, get_usermap, get_users_with_permission, populate_roles, usermap_row_to_dict
import datetime as dt
from .globals import get_permissions, get_tenant_single
from .emails import email_accept_applicant


@anvil.server.callable(require_user=True)
def create_tenant_single():
    """Create a tenant."""
    user = anvil.users.get_user(allow_remembered=True)
    if len(app_tables.tenants.search()) != 0:
        return None

    tenant = app_tables.tenants.add_row()
    _ = populate_roles(tenant)
    admin_role = app_tables.roles.get(tenant=tenant, name='Admin')
    _ = app_tables.usermap.add_row(tenant=tenant, user=user, roles=[admin_role])
    return get_tenant_single(user, tenant)
    

@anvil.server.callable(require_user=True)
def join_tenant(tenant_id):
    """Join a tenant by its database row id."""
    # Kind of unnecessary as get_usermap joins the tenant.
    user = anvil.users.get_user(allow_remembered=True)
    tenant = app_tables.tenants.get_by_id(tenant_id)
    usermap = get_usermap(tenant_id, user, tenant)
    return usermap


@anvil.server.callable(require_user=True)
def leave_tenant():
    """Leave a tenant."""
    pass


@anvil.server.callable(require_user=True)
def delete_user(tenant_id, user_email):
    print_timestamp('delete_user')
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('delete_user_bk', tenant_id, user, user_email)


@anvil.server.background_task
def delete_user_bk(tenant_id, user, user_email):
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        return None
    
    user_del = app_tables.users.get(email=user_email)
    user_del_tenant, user_del_usermap, user_del_permissions = validate_user(tenant_id, user_del)
    
    if 'delete_members' in user_del_permissions and 'delete_admin' not in permissions:
        raise Exception("Only users with the delete_admin permission can delete this user.")

    # Only have the power to delete a user from your group, not from the app entirely.
    user_del_usermap.delete()


@anvil.server.callable(require_user=True)
def edit_member(tenant_id, new_dict):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    member = app_tables.users.get(email=new_dict['email'])
    _, membermap, _ = validate_user(tenant_id, member, tenant=tenant)

    if user == member or 'edit_members' in permissions:
        membermap['first_name'] = new_dict['first_name']
        membermap['last_name'] = new_dict['last_name']
        membermap['phone'] = new_dict['phone']
        membermap['discord'] = new_dict['discord']
        membermap['booking_link'] = new_dict['booking_link']
        membermap['consent_check'] = new_dict['consent_check']

    if 'edit_members' in permissions:
        roles = app_tables.roles.search(tenant=tenant, name=q.any_of(*new_dict['roles']))
        membermap['roles'] = list(roles)
        # print_timestamp('len of roles')
        # print(membermap['roles'])
        if len(membermap['roles']) == 0:
            membermap['roles'] = None

    if 'see_members' in permissions:
        membermap['notes'] = new_dict['notes']

    return usermap_row_to_dict(membermap)


@anvil.server.callable(require_user=True)
def save_user_notes(tenant_id, user_email, new_note):
    """Save user notes."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('save_user_notes_bk', tenant_id, user, user_email, new_note)


@anvil.server.background_task
def save_user_notes_bk(tenant_id, user, user_email, new_note):
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' in permissions:
        member_user = app_tables.users.get(email=user_email)
        member_usermap = app_tables.usermap.get(user=member_user, tenant=tenant)
        member_usermap['notes'] = new_note


# @anvil.server.callable(require_user=True)
# def add_role_to_member(tenant_id, role_name, member_email):
#     """Add volunteer role to member."""
#     user = anvil.users.get_user(allow_remembered=True)
#     anvil.server.launch_background_task('add_role_to_member_bk', tenant_id, user, role_name, member_email)


# @anvil.server.background_task
# def add_role_to_member_bk(tenant_id, user, role_name, member_email):
#     tenant, usermap, permissions = validate_user(tenant_id, user)

#     if 'edit_members' not in permissions:
#         return None

#     role = app_tables.roles.get(name=role_name, tenant=tenant)
#     role['last_update'] = dt.date.today()
#     member = app_tables.users.get(tenant=tenant, email=member_email)
    
#     member_usermap = get_usermap(member)
#     if member_usermap['roles']:
#         if [role] not in member_usermap['roles']:
#             print('adding additional role')
#             member_usermap['roles'] += [role]
#     else:
#         member_usermap['roles'] = [role]
#     return member_usermap


@anvil.server.callable(require_user=True)
def remove_role_from_member(tenant_id, role_name, member_email):
    """Remove volunteer role from member."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('remove_role_from_member_bk', tenant_id, user, role_name, member_email)


@anvil.server.background_task
def remove_role_from_member_bk(tenant_id, user, role_name, member_email):
    tenant, usermap, permissions = validate_user(tenant_id, user)

    if 'edit_members' not in permissions:
        return None
    
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    role['last_update'] = dt.date.today()
    member = app_tables.users.get(tenant=tenant, email=member_email)
    member_usermap = get_usermap(member)
    member_usermap['roles'] = [i for i in member_usermap['roles'] if i != role]
    return member_usermap


@anvil.server.callable(require_user=True)
def add_role(tenant_id, role_name, role_perms):
    """Add volunteer role definition."""
    from .helpers import role_row_to_dict
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    if 'edit_roles' not in permissions:
        return None

    perm_rows = app_tables.permissions.search(name=q.any_of(*role_perms))
    if not app_tables.roles.get(tenant=tenant, name=role_name):
        _ = app_tables.roles.add_row(
            name=role_name, tenant=tenant,
            last_update=dt.date.today(),
            can_edit=True,
            permissions=list(perm_rows)
        )
        return [role_row_to_dict(role) for role in app_tables.roles.search(tenant=tenant)]


@anvil.server.callable(require_user=True)
def get_role_guides(tenant_id, role_name):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    return app_tables.rolefiles.search(role=role)


@anvil.server.callable(require_user=True)
def upload_role_guide(tenant_id, role_name, file):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    
    role = app_tables.roles.get(name=role_name, tenant=tenant, can_edit=True)
    _ = app_tables.rolefiles.add_row(role=role, name=file.name, file=file)
    return app_tables.rolefiles.search(role=role)


@anvil.server.callable(require_user=True)
def delete_role_guide(tenant_id, role_name, guide_name):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    role = app_tables.roles.get(name=role_name, tenant=tenant, can_edit=True)
    guide = app_tables.rolefiles.get(role=role, name=guide_name)
    guide.delete()
    return app_tables.rolefiles.search(role=role)


@anvil.server.callable(require_user=True)
def update_role(tenant_id, role_name, new_role_dict):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    role = app_tables.roles.get(name=role_name, tenant=tenant, can_edit=True)
    for key in ['name']:
            role[key] = new_role_dict[key]
    role['last_update'] = dt.date.today()
    perm_rows = app_tables.permissions.search(name=q.any_of(*new_role_dict['permissions']))
    role['permissions'] = list(perm_rows)


# @anvil.server.callable(require_user=True)
# def save_user_roles(tenant_id, email, new_roles):
#     user = anvil.users.get_user(allow_remembered=True)
#     tenant, usermap, permissions = validate_user(tenant_id, user)
#     if 'edit_members' not in permissions:
#         return None
    
#     roles = app_tables.roles.search(tenant=tenant, name=q.any_of(*new_roles))
    
#     member_user = app_tables.users.get(email=email)
#     member_usermap = app_tables.usermap.get(tenant=tenant, user=member_user)
#     member_usermap['roles'] = list(roles)
#     return member_usermap


@anvil.server.callable(require_user=True)
def search_users_by_text(tenant_id, search_string):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []
    
    users = app_tables.users.search(
        q.fetch_only('email', 'first_name', 'last_name'),
        q.any_of(
            email=q.ilike('%'+search_string+'%'),
            first_name=q.ilike('%'+search_string+'%'),
            last_name=q.ilike('%'+search_string+'%')
        )
    )
    usermaps = app_tables.usermap.search(
        q.fetch_only(
            'user',
            user=q.fetch_only(
                'email', 'first_name', 'last_name', 'last_login', 'signed_up'
            )
        ),
        q.any_of(
            user=q.any_of(*users),
            notes=q.ilike('%'+search_string+'%')
        ),
        tenant=tenant
    )
    return usermaps


@anvil.server.callable(require_user=True)
def get_member_data(tenant_id, email):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    member = app_tables.users.get(
        q.fetch_only('email'),
        email=email
    )
    
    if 'see_members' in permissions:
        membermap = app_tables.usermap.get(tenant=tenant, user=member)
        membermap_dict = usermap_row_to_dict(membermap)
    else:
        membermap = app_tables.usermap.get(tenant=tenant, user=user)
        membermap_dict = usermap_row_to_dict(membermap)
        membermap_dict['notes'] = ''

    return membermap_dict
    

@anvil.server.callable(require_user=True)
def search_users_by_role(tenant_id, role_name):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []

    if role_name:
        role = q.any_of([app_tables.roles.get(tenant=tenant, name=role_name)])
    else:
        role = None

    usermaps = app_tables.usermap.search(
        q.fetch_only(
            'user',
            user=q.fetch_only(
                'email', 'first_name', 'last_name', 'last_login', 'signed_up'
            )
        ),
        roles=role,
        tenant=tenant
    )
    return usermaps


@anvil.server.callable(require_user=True)
def accept_applicant(tenant_id, email):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    if 'see_members' not in permissions:
        return None

    member_user = app_tables.users.get(email=email)
    member_usermap = app_tables.usermap.get(user=member_user, tenant=tenant)
    member_usermap['roles'] = [app_tables.roles.get(tenant=tenant, name='Approved')]

    email_accept_applicant(tenant, member_user['email'])
    return usermap_row_to_dict(member_usermap)


@anvil.server.callable(require_user=True)
def reject_applicant(tenant_id, email):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    if 'see_members' not in permissions:
        return None

    member_user = app_tables.users.get(email=email)
    member_usermap = app_tables.usermap.get(user=member_user, tenant=tenant)
    member_usermap['roles'] = None
    return usermap_row_to_dict(member_usermap)


@anvil.server.callable(require_user=True)
def generate_secret():
    import secrets
    import string
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(20))


@anvil.server.callable(require_user=True)
def update_tenant_data(tenant_id, new_dict):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        return None
    print(new_dict['name'])
    for safe_key in ['name', 'waiver', 'logo', 'discord_invite',
                     'paypal_plans', 'discourse_url', 'new_roles']:
        tenant[safe_key] = new_dict[safe_key]

    secrets = ['discourse_api_key', 'discourse_secret',
               'paypal_client_id', 'paypal_secret', 'paypal_webhook_id']
    for secret_key in secrets:
        tenant[secret_key] = anvil.secrets.encrypt_with_key('encryption_key', new_dict[secret_key])