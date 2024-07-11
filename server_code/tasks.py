import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.email
import anvil.secrets

from .helpers import print_timestamp, verify_tenant, validate_user, get_usermap, get_users_with_permission, populate_roles, usermap_row_to_dict
import datetime as dt
from .globals import get_permissions, get_tenant_single


def clean_up_user(user):
    if not user['first_name']:
        user['first_name'] = ''
    if not user['last_name']:
        user['last_name'] = ''
    if not user['fb_url']:
        user['fb_url'] = ''
    if not user['discord']:
        user['discord'] = ''
    return user


@anvil.server.background_task
def clean_up_users():
    for user in app_tables.users.search(first_name=None):
        user['first_name'] = ''
    for user in app_tables.users.search(last_name=None):
        user['last_name'] = ''
    for user in app_tables.users.search(fb_url=None):
        user['fb_url'] = ''
    for user in app_tables.users.search(discord=None):
        user['discord'] = ''


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


@anvil.server.background_task
def email_accept_applicant(tenant, email):
    """Send an email to an applicant upon acceptance."""

    msg_body = f"""
    <p>Hi! This is an automated message from the {tenant['name']} community platform.</p>

    <p>Your application to join the group has been accepted!</p>

    <p>Please log into the app for next steps (see link below). Fill out your profile, read the community guidelines, and make the membership payment.</p>

    <p>{anvil.server.get_app_origin()}</p>
    
    <p>Regards,</p>
    <p>{tenant['name']} via the NotAlone Platform.</p>
    """

    screeners = get_users_with_permission(None, 'see_members', tenant)
    screener_list = [i['user']['email'] for i in screeners]
    anvil.email.send(
        to=email,
        bcc=screener_list,
        from_address="noreply",
        from_name="noreply",
        subject=f"Welcome to the {tenant['name']} Community!",
        html=msg_body
    )


@anvil.server.callable(require_user=True)
def add_role_to_member(tenant_id, role_name, member_email):
    """Add volunteer role to member."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('add_role_to_member_bk', tenant_id, user, role_name, member_email)


@anvil.server.background_task
def add_role_to_member_bk(tenant_id, user, role_name, member_email):
    tenant, usermap, permissions = validate_user(tenant_id, user)

    if 'edit_members' not in permissions:
        return None

    role = app_tables.roles.get(name=role_name, tenant=tenant)
    role['last_update'] = dt.date.today()
    member = app_tables.users.get(tenant=tenant, email=member_email)
    
    member_usermap = get_usermap(member)
    if member_usermap['roles']:
        if [role] not in member_usermap['roles']:
            print('adding additional role')
            member_usermap['roles'] += [role]
    else:
        member_usermap['roles'] = [role]
    return member_usermap


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
def add_role(tenant_id, role_name, reports_to, role_members):
    """Add volunteer role definition."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('add_role_bk', tenant_id, user, role_name, reports_to, role_members)


@anvil.server.background_task
def add_role_bk(tenant_id, user, role_name, reports_to, role_members):
    tenant, usermap, permissions = validate_user(tenant_id, user)

    if 'edit_roles' not in permissions:
        return None

    if not app_tables.roles.get(tenant=tenant, name=role_name):
        app_tables.roles.add_row(name=role_name, reports_to=reports_to, tenant=tenant, last_update=dt.date.today(), can_edit=True)


@anvil.server.callable(require_user=True)
def upload_role_guide(tenant_id, role_name, file):
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('upload_role_guide_bk', tenant_id, user, role_name, file)


@anvil.server.background_task
def upload_role_guide_bk(tenant_id, user, role_name, file):
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    # TODO: allow multiple files
    if role['can_edit']:
        role['guide'] = file


@anvil.server.callable(require_user=True)
def update_role(tenant_id, role_name, new_role_dict):
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('update_role_bk', tenant_id, user, role_name, new_role_dict)


@anvil.server.background_task
def update_role_bk(tenant_id, user, role_name, new_role_dict):
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    if role['can_edit']:
        for key, val in new_role_dict.items():
            role[key] = val


@anvil.server.callable(require_user=True)
def save_user_roles(tenant_id, email, new_roles):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'edit_members' not in permissions:
        return None
    
    roles = app_tables.roles.search(tenant=tenant, name=q.any_of(*new_roles))
    
    member_user = app_tables.users.get(email=email)
    member_usermap = app_tables.usermap.get(tenant=tenant, user=member_user)
    member_usermap['roles'] = list(roles)
    return member_usermap


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
        notes = membermap['notes']
    else:
        membermap = app_tables.usermap.get(tenant=tenant, user=user)
        notes = None

    return usermap_row_to_dict(membermap, notes)
    

@anvil.server.callable(require_user=True)
def search_users_by_role(tenant_id, role_name):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' not in permissions:
        return []

    role = None
    if role_name:
        role = q.any_of([app_tables.roles.get(tenant=tenant, name=role_name)])

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
    for safe_key in ['name', 'waiver', 'logo', 'discord_invite', 'paypal_plans', 'discourse_url']:
        tenant[safe_key] = new_dict[safe_key]

    for secret_key in ['discourse_api_key', 'discourse_secret', 'paypal_client_id', 'paypal_secret']:
        tenant[secret_key] = anvil.secrets.encrypt_with_key('encryption_key', new_dict[secret_key])