import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.email

from .helpers import print_timestamp, verify_tenant, validate_user, get_usermap, populate_roles, get_users_with_permission
import datetime as dt
from anvil_extras import authorisation
from anvil_extras.authorisation import authorisation_required

authorisation.set_config(get_roles='usermap')


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
def join_tenant(tenant_id):
    """Join a tenant by its database row id."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = get_usermap(user)
    tenant = app_tables.tenants.get_by_id(tenant_id)
    if usermap['tenants'] is None:
        usermap['tenants'] = [tenant]
        # Now let the user book an interview
        new_role = app_tables.roles.get(tenant=tenant, name='Applicant')
        if not new_role:
            populate_roles(tenant)
        usermap['roles'] = [app_tables.roles.get(tenant=tenant, name='Applicant')]
    # TODO: elif for adding a user to another tenant
    return user


@anvil.server.callable(require_user=True)
def leave_tenant():
    """Leave a tenant."""
    pass


@anvil.server.callable(require_user=True)
def update_user(tenant_id, user_dict):
    user = anvil.users.get_user(allow_remembered=True)
    verify_tenant(tenant_id, user)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'consent_check', 'paypal_sub_id', 'phone', 'discord']:
        if user[key] != user_dict[key]:
            user[key] = user_dict[key]
    user = clean_up_user(user)
    return user


@anvil.server.callable(require_user=True)
def update_member(tenant_id, email, col_dict):
    """Update roles for a member."""
    print_timestamp('update_member: ' + email + ' col_dict: ' + str(col_dict))
    user = anvil.users.get_user(allow_remembered=True)
    usermap, permissions, tenant = validate_user(tenant_id, user)

    member_user = app_tables.users.get(email=email)
    member_usermap = app_tables.users.get(user=member_user, tenant=tenant)
    if 'see_members' in permissions:
        pass
    elif 'see_applicants' in permissions:
        pass
    elif 'edit_members' in permissions:
        pass
    else:
        raise Exception('Authorisation required.')
    # TODO: complete this function


@anvil.server.callable(require_user=True)
@authorisation_required('delete_members')
def delete_user(tenant_id, user_email):
    print_timestamp('delete_user')
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('delete_user_bk', tenant_id, user, user_email)


@anvil.server.background_task
def delete_user_bk(tenant_id, user, user_email):
    usermap, permissions, tenant = validate_user(tenant_id, user)
    if 'delete_members' not in permissions:
        return None
    
    user_del = app_tables.users.get(email=user_email)
    user_del_usermap, user_del_permissions, user_del_tenant = validate_user(tenant_id, user_del)
    
    if 'delete_members' in user_del_permissions and 'delete_admin' not in permissions:
        raise Exception("Only users with the delete_admin permission can delete this user.")
    
    if len(user_del_usermap['tenants']) > 1:
        # If user is on multiple tenants, just remove them from this tenant.
        user_del_usermap['tenants'] = [i for i in user_del_usermap['tenants'] if i.get_id() != tenant_id]
    else:
        user_del.delete()


@anvil.server.callable(require_user=True)
@authorisation_required('see_applicants')
def save_user_notes(tenant_id, user_email, new_note):
    """Save user notes."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('save_user_notes_bk', tenant_id, user, user_email, new_note)


@anvil.server.background_task
def save_user_notes_bk(tenant_id, user, user_email, new_note):
    usermap, permissions, tenant = validate_user(tenant_id, user)
    if 'see_applicants' in permissions:
        user_row = app_tables.users.get(email=user_email)
        note_row = app_tables.notes.get(user=user_row, tenant=tenant)
        note_row['notes'] = new_note


@anvil.server.callable(require_user=True)
@authorisation_required('see_applicants')
def notify_accept(tenant_id, email_to):
    """Notify the applicant they've been accepted."""
    # TODO: roll this into one function for approving an applicant.
    print_timestamp('notify_accept: ' + email_to)
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('notify_accept_bk', tenant_id, user, email_to)


@anvil.server.background_task
def notify_accept_bk(tenant_id, user, email_to):
    """Send an email to an applicant upon acceptance."""
    usermap, permissions, tenant = validate_user(tenant_id, user)

    if 'see_applicants' not in permissions:
        return None

    msg_body = f"""
    <p>Hi! This is an automated message from the {tenant['name']} community platform.</p>

    <p>You have passed the screening interview!</p>

    <p>Please log into the app for next steps (see link below). Fill out your profile, read the community guidelines, and make the membership payment.</p>

    <p>{anvil.server.get_app_origin()}</p>
    
    <p>Regards,</p>
    <p>NotAlone team.</p>
    """

    screeners = get_users_with_permission(tenant_id, 'see_applicants', tenant)
    screener_list = [i['user']['email'] for i in screeners]
    anvil.email.send(
        to=email_to,
        bcc=screener_list,
        from_address="noreply",
        from_name="noreply",
        subject=f"Welcome to the {tenant['name']} Community!",
        html=msg_body
    )


@anvil.server.callable(require_user=True)
@authorisation_required('edit_members')
def add_role_to_member(tenant_id, role_name, member_email):
    """Add volunteer role to member."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('add_role_to_member_bk', tenant_id, user, role_name, member_email)


@anvil.server.background_task
def add_role_to_member_bk(tenant_id, user, role_name, member_email):
    usermap, permissions, tenant = validate_user(tenant_id, user)

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
@authorisation_required('edit_members')
def remove_role_from_member(tenant_id, role_name, member_email):
    """Remove volunteer role from member."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('remove_role_from_member_bk', tenant_id, user, role_name, member_email)


@anvil.server.background_task
def remove_role_from_member_bk(tenant_id, user, role_name, member_email):
    usermap, permissions, tenant = validate_user(tenant_id, user)

    if 'edit_members' not in permissions:
        return None
    
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    role['last_update'] = dt.date.today()
    member = app_tables.users.get(tenant=tenant, email=member_email)
    member_usermap = get_usermap(member)
    member_usermap['roles'] = [i for i in member_usermap['roles'] if i != role]
    return member_usermap


@anvil.server.callable(require_user=True)
@authorisation_required('edit_roles')
def add_role(tenant_id, role_name, reports_to, role_members):
    """Add volunteer role definition."""
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('add_role_bk', tenant_id, user, role_name, reports_to, role_members)


@anvil.server.background_task
def add_role_bk(tenant_id, user, role_name, reports_to, role_members):
    usermap, permissions, tenant = validate_user(tenant_id, user)

    if 'edit_roles' not in permissions:
        return None

    if not app_tables.roles.get(tenant=tenant, name=role_name):
        app_tables.roles.add_row(name=role_name, reports_to=reports_to, tenant=tenant, last_update=dt.date.today(), can_edit=True)


@anvil.server.callable(require_user=True)
@authorisation_required('edit_roles')
def upload_role_guide(tenant_id, role_name, file):
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('upload_role_guide_bk', tenant_id, user, role_name, file)


@anvil.server.background_task
def upload_role_guide_bk(tenant_id, user, role_name, file):
    usermap, permissions, tenant = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    # TODO: allow multiple files
    if role['can_edit']:
        role['guide'] = file


# @anvil.server.callable(require_user=True)
# @authorisation_required('see_forum')
# def download_role_guide(tenant_id, role_name):
#     user = anvil.users.get_user(allow_remembered=True)
#     usermap, permissions, tenant = validate_user(tenant_id, user)
#     role = app_tables.roles.get(name=role_name, tenant=tenant)
#     return role['guide']


@anvil.server.callable(require_user=True)
@authorisation_required('edit_roles')
def update_role(tenant_id, role_name, new_role_dict):
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('update_role_bk', tenant_id, user, role_name, new_role_dict)

@anvil.server.background_task
def update_role_bk(tenant_id, user, role_name, new_role_dict):
    usermap, permissions, tenant = validate_user(tenant_id, user)
    if 'edit_roles' not in permissions:
        return None
    role = app_tables.roles.get(name=role_name, tenant=tenant)
    if role['can_edit']:
        for key, val in new_role_dict.items():
            role[key] = val


# -------------------------
# Temp stuff for migration
# -------------------------
def migrate_tables():
    users = app_tables.users.search(tenant=q.not_(None))
    for user in users:
        usermap = app_tables.usermap.get(user=user)
        if not usermap:
            usermap = app_tables.usermap.add_row(user=user)
        if user['tenant'] and not usermap['tenants']:
            usermap['tenants'] = [user['tenant']]
        usermap['roles'] = user['roles']
