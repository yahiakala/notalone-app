import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.email

from .helpers import permission_required, print_timestamp, verify_tenant
from .gets import _get_usermap, _get_permissions
import datetime as dt


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
def join_tenant(id):
    """Join a tenant by its database row id."""
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        user['tenant'] = app_tables.tenants.get_by_id(id)
        # Now let the user book an interview
        user['auth_booking'] = True
    return user


# @anvil.server.callable(require_user=True)
# def leave_tenant():
#     """Leave a tenant - used for test code."""
#     user = anvil.users.get_user(allow_remembered=True)
#     for key, val in user.items():
#         if 'auth_' in key and 'auth_dev' not in key:
#             user[key] = False
#     user['tenant'] = None
#     return user


@anvil.server.callable(require_user=True)
def update_user(user_dict, tenant_id):
    user = anvil.users.get_user(allow_remembered=True)
    verify_tenant(user, tenant_id)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'consent_check', 'paypal_sub_id', 'phone', 'discord']:
        if user[key] != user_dict[key]:
            user[key] = user_dict[key]
    user = clean_up_user(user)
    return user


@anvil.server.callable(require_user=True)
def update_member(email, col_dict, tenant_id):
    """Reset roles for a member."""
    print_timestamp('update_member: ' + email + ' col_dict: ' + str(col_dict))
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    verify_tenant(user, tenant_id, usermap)
    
    member = app_tables.users.get(email=email, tenant=user['tenant'])
    if 'see_members' in permissions:
        acceptable_cols = None
    elif 'see_applicants' in permissions:
        acceptable_cols = ['auth_profile', 'auth_forumchat', 'auth_booking']
    else:
        raise Exception('Authorisation required.')

    for col_name, val in col_dict.items():
        if (acceptable_cols is not None and col_name in acceptable_cols) or acceptable_cols is None:
            member[col_name] = val
    return member


@anvil.server.callable(require_user=True)
def delete_user(user_dict, tenant_id):
    print_timestamp('delete_user')
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    verify_tenant(user, tenant_id, usermap)
    if 'delete_members' in permissions:
        user_del = app_tables.users.get(email=user_dict['email'])
        user_del_usermap = _get_usermap(user_del)
        user_del_permissions = _get_permissions(user_del, tenant_id, user_del_usermap)
        verify_tenant(user_del, tenant_id, user_del_usermap)
        if 'delete_members' in user_del_permissions and 'delete_admin' not in permissions:
            raise Exception("Only users with the delete_admin permission can delete this user.")
        if len(user_del_usermap['tenant']) > 1:
            # If user is on multiple tenants, just remove them from this tenant.
            user_del_usermap['tenant'] = [i for i in user_del_usermap['tenant'] if i.get_id() != tenant_id]
        else:
            user_del.delete()


def user_search(search_txt, tenant_id):
    """Search for a user by name, email, or notes."""
    # TODO: deprecate this, move to client side logic.
    print_timestamp('user_search: ' + search_txt)
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, usermap)
    verify_tenant(user, tenant_id, usermap)
    emails = set()
    for note in app_tables.notes.search(tenant=user['tenant'], notes=q.ilike('%' + search_txt + '%')):
        emails.add(note['user']['email'])
    emails = list(emails)
    
    users = app_tables.users.search(
        q.any_of(
            first_name=q.ilike(search_txt),
            last_name=q.ilike(search_txt),
            email=q.any_of(
                q.ilike(search_txt),
                q.any_of(*emails)
            )
        ),
        tenant=user['tenant']
    )
    users_list = [
        {
            'first_name': member['first_name'],
            'last_name': member['last_name'],
            'email': member['email'],
            'fb_url': member['fb_url'],
            'discord': member['discord'],
            'fee': member['fee'],
            'good_standing': member['good_standing'],
            'last_login': member['last_login'],
            'signed_up': member['signed_up'],
            'paypal_sub_id': member['paypal_sub_id'],
            'auth_screenings': member['auth_screenings'],
            'auth_forumchat': member['auth_forumchat'],
            'auth_profile': member['auth_profile'],
            'auth_booking': member['auth_booking'],
            'auth_members': member['auth_members'],
            'auth_dev': member['auth_dev']
        }
        for member in users
    ]
    print_timestamp('user_search: ' + search_txt + ' done')
    return users_list


@anvil.server.callable(require_user=True)
def get_user_notes(email, tenant_id):
    """Get the notes for a particular user."""
    # TODO: incorporate into the main get_user_data
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    _ = verify_tenant(user, tenant_id, usermap)
    if 'see_members' in permissions or 'see_applicants' in permissions:
        user_row = app_tables.users.get(email=email, tenant=user['tenant'])
        note_row = app_tables.notes.get(user=user_row, tenant=user['tenant'])
        if note_row:
            return note_row
        else:
            return app_tables.notes.add_row(user=user_row, notes='', tenant=user['tenant'])


@anvil.server.callable(require_user=True)
def save_user_notes(tenant_id, user_email, new_note):
    """Save user notes."""
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    _ = verify_tenant(user, tenant_id, usermap)
    if 'see_applicants' in permissions:
        user_row = app_tables.users.get(email=user_email, tenant=user['tenant'])
        note_row = app_tables.notes.get(user=user_row, tenant=user['tenant'])
        note_row['notes'] = new_note


@anvil.server.callable(require_user=True)
def notify_accept(tenant_id, email_to):
    """Notify the applicant they've been accepted."""
    print_timestamp('notify_accept: ' + email_to)
    user = anvil.users.get_user(allow_remembered=True)
    anvil.server.launch_background_task('notify_accept_bk', tenant_id, user, email_to)


@anvil.server.background_task
def notify_accept_bk(tenant_id, user, email_to):
    """Send an email to an applicant upon acceptance."""
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, tenant_id, usermap)
    tenant = verify_tenant(user, tenant_id, usermap)
    
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
    
    screeners = app_tables.users.search(auth_screenings=True, tenant=tenant)
    screener_list = [i['email'] for i in screeners]
    anvil.email.send(
        to=email_to,
        bcc=screener_list,
        from_address="noreply",
        from_name="noreply",
        subject=f"Welcome to the {tenant['name']} Community!",
        html=msg_body
    )


@permission_required('auth_members')
def add_role_to_member(role_name, member_email):
    """Add volunteer role to member."""
    user = anvil.users.get_user(allow_remembered=True)
    role = app_tables.roles.get(name=role_name, tenant=user['tenant'])
    role['last_update'] = dt.date.today()
    member = app_tables.users.get(tenant=user['tenant'], email=member_email)
    # member['roles'] += [role]
    if member['roles']:
        if [role] not in member['roles']:
            print('adding additional role')
            member['roles'] += [role]
    else:
        member['roles'] = [role]
    return member


@permission_required('auth_members')
def remove_role_from_member(role_name, member_email):
    """Remove volunteer role from member."""
    user = anvil.users.get_user(allow_remembered=True)
    role = app_tables.roles.get(name=role_name, tenant=user['tenant'])
    role['last_update'] = dt.date.today()
    member = app_tables.users.get(tenant=user['tenant'], email=member_email)
    member['roles'] = [i for i in member['roles'] if i != role]


@permission_required('auth_members')
def add_role(role_name, reports_to, role_members):
    """Add volunteer role definition."""
    user = anvil.users.get_user(allow_remembered=True)
    if not app_tables.roles.get(tenant=user['tenant'], name=role_name):
        app_tables.roles.add_row(name=role_name, reports_to=reports_to, tenant=user['tenant'], last_update=dt.date.today())
    role_members.append(
        {
            'name': role_name,
            'last_update': dt.date.today(),
            'reports_to': reports_to,
            'member': []
            # 'users': role_members[-1]['users']
        }
    )
    return role_members


@permission_required('auth_members')
def upload_role_guide(role_name, file):
    user = anvil.users.get_user(allow_remembered=True)
    role = app_tables.roles.get(name=role_name, tenant=user['tenant'])
    role['guide'] = file


@permission_required('auth_forumchat')
def download_role_guide(role_name):
    user = anvil.users.get_user(allow_remembered=True)
    role = app_tables.roles.get(name=role_name, tenant=user['tenant'])
    return role['guide']


@permission_required('auth_members')
def update_role(role_name, new_role_dict):
    user = anvil.users.get_user(allow_remembered=True)
    role = app_tables.roles.get(name=role_name, tenant=user['tenant'])
    for key, val in new_role_dict.items():
        role[key] = val


def populate_permissions():
    """Populate the permissions table."""
    permissions = [
        'see_applicants',
        'see_members',
        'see_profile',
        'see_forum',
        'book_interview',
        'see_finances',
        'dev'
    ]
    if len(app_tables.permissions.search()) == 0:
        for perm in permissions:
            app_tables.permissions.add_row(name=perm)