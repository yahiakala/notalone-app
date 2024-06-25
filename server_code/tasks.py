import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.email

from .helpers import permission_required, print_timestamp

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
def get_tenants():
    """Get a list of tenants for joining purposes."""
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        return app_tables.tenants.client_readable(q.only_cols('name'))
    else:
        return []


@anvil.server.callable(require_user=True)
def join_tenant(id):
    """Join a tenant by its database row id."""
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        user['tenant'] = app_tables.tenants.get_by_id(id)
        # Now let the user book an interview
        user['auth_booking'] = True
    return user


@anvil.server.callable(require_user=True)
def leave_tenant():
    """Leave a tenant - used for test code."""
    user = anvil.users.get_user(allow_remembered=True)
    for key, val in user.items():
        if 'auth_' in key and 'auth_dev' not in key:
            user[key] = False
    user['tenant'] = None
    return user

def verify_tenant(user, tenant_id, usermap=None):
    """Verify a user is in this tenant."""
    tenant_row = app_tables.tenants.get_by_id(tenant_id)
    usermap = usermap or app_tables.usermap.get(user=user)
    # TODO: might cause an error if none or just 1 tenant
    if tenant_row not in usermap['tenant']:
        raise Exception('User does not belong to this tenant.')


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


@anvil.server.callable(require_user=True)
def get_users(tenant_id):
    """Get a full list of the users."""
    print_timestamp('get_users')
    user = anvil.users.get_user(allow_remembered=True)
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, usermap)
    verify_tenant(user, tenant_id, usermap)
    if 'see_members' in permissions:
        user = anvil.users.get_user(allow_remembered=True)
        return _get_users(user)
    else:
        return []


def _get_users(user):
    memberlist = [
        {
            'first_name': member['first_name'] or '',
            'last_name': member['last_name'] or '',
            'email': member['email'],
            'fb_url': member['fb_url'] or '',
            'discord': member['discord'] or '',
            'fee': member['fee'],
            'payment_status': member['payment_status'],
            'payment_expiry': member['payment_expiry'],
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
        for member in app_tables.users.search(tenant=user['tenant'])
    ]
    print_timestamp('done get_users')
    return memberlist


@anvil.server.callable(require_user=True)
@authorisation_required('see_members')
def user_search(search_txt, tenant_id):
    """Search for a user by name, email, or notes."""
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


@permission_required(['auth_members', 'auth_screenings'])
def get_user_notes(email):
    """Get the notes for a particular user."""
    user = anvil.users.get_user(allow_remembered=True)
    user_row = app_tables.users.get(email=email, tenant=user['tenant'])
    note_row = app_tables.notes.get(user=user_row, tenant=user['tenant'])
    if note_row:
        return note_row
    else:
        return app_tables.notes.add_row(user=user_row, notes='', tenant=user['tenant'])


@permission_required(['auth_members', 'auth_screenings'])
def save_user_notes(user_email, new_note):
    """Save user notes."""
    user = anvil.users.get_user(allow_remembered=True)
    user_row = app_tables.users.get(email=user_email, tenant=user['tenant'])
    note_row = app_tables.notes.get(user=user_row, tenant=user['tenant'])
    note_row['notes'] = new_note


@permission_required(['auth_screenings', 'auth_members'])
def get_applicants():
    """Get applicants."""
    # TODO: break this up into two funcs
    print_timestamp('get_applicants')
    user = anvil.users.get_user(allow_remembered=True)
    return _get_applicants(user)


def _get_applicants(user):
    app_q = app_tables.users.search(
        q.fetch_only("email", "first_name", "last_name", "auth_profile",
                    "auth_forumchat", "auth_booking", "good_standing", "signed_up"),
        tenant=user['tenant'],
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


@permission_required('auth_booking')
def get_screener_link():
    """Get random screener."""
    import random
    user = anvil.users.get_user(allow_remembered=True)
    # return random.choice(
    #     [
    #         {
    #             'first_name': r['first_name'],
    #             'booking_link': r['booking_link'],
    #         }
    #         for r in app_tables.users.search(booking_link=q.not_(None),
    #                                          tenant=user['tenant'],
    #                                          auth_screenings=True)
    #     ]
    # )
    # Trying a better method to be random
    records = [
        {
            'first_name': r['first_name'],
            'booking_link': r['booking_link'],
        }
        for r in app_tables.users.search(booking_link=q.not_(None),
                                         tenant=user['tenant'],
                                         auth_screenings=True)
    ]
    # Shuffle the records list
    random.shuffle(records)
    return random.choice(records)


@permission_required('auth_members')
def get_finances():
    """Get financial info."""
    user = anvil.users.get_user(allow_remembered=True)
    data = app_tables.finances.get(tenant=user['tenant'])
    return {
        'rev_12': data['rev_12'] or 0,
        'budgets': data['budgets'] or {},
        'rev_12_active': data['rev_12_active'] or 0
    }


@permission_required('auth_forumchat')
def get_forumlink():
    """Get financial info."""
    user = anvil.users.get_user(allow_remembered=True)
    return 'https://' + app_tables.forum.get(tenant=user['tenant'])['discourse_url']


@anvil.server.callable(require_user=True)
def get_discordlink():
    user = anvil.users.get_user(allow_remembered=True)
    if user['auth_forumchat']:
        return app_tables.forum.get(tenant=user['tenant'])['discord_invite']
    return ''


@permission_required('auth_screenings')
def notify_accept(email_to):
    """Notify the applicant they've been accepted."""
    print_timestamp('notify_accept: ' + email_to)
    user = anvil.users.get_user(allow_remembered=True)
    msg_body = f"""
    <p>Hi! This is an automated message from the {user['tenant']['name']} community platform.</p>
    
    <p>You have passed the screening interview!</p>

    <p>Please log into the app for next steps (see link below). Fill out your profile, read the community guidelines, and make the membership payment.</p>

    <p>{anvil.server.get_app_origin()}</p>
    
    <p>Regards,</p>
    <p>NotAlone team.</p>
    """
    
    screeners = app_tables.users.search(auth_screenings=True, tenant=user['tenant'])
    screener_list = [i['email'] for i in screeners]
    anvil.email.send(
        to=email_to,
        bcc=screener_list,
        from_address="noreply",
        from_name="noreply",
        subject=f"Welcome to the {user['tenant']['name']} Community!",
        html=msg_body
    )


@permission_required('auth_forumchat')
def get_roles():
    """Get volunteer roles."""
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.roles.search(tenant=user['tenant'])


@permission_required('auth_members')
def get_roles_to_members():
    """Get a dict that maps volunteer roles to users."""
    user = anvil.users.get_user(allow_remembered=True)
    role_members = []
    users = list(app_tables.users.search(tenant=user['tenant']))
    for role in app_tables.roles.search(tenant=user['tenant']):
        role_members.append(
            {
                'name': role['name'],
                'last_update': role['last_update'],
                'reports_to': role['reports_to'],
                'member': [i for i in app_tables.users.search(tenant=user['tenant'], roles=[role])]
                # 'users': users
            }
        )
    return role_members

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


@anvil.server.callable(require_user=True)
def get_super_load():
    user = anvil.users.get_user(allow_remembered=True)
    data = {'users': [], 'applicants': []}
    if user['auth_members']:
        data['users'] = get_users()
    if user['auth_screenings'] or user['auth_members']:
        data['applicants'] = get_applicants()
    return data


@anvil.server.callable(require_user=True)
def get_user_data(tenant_id):
    print_timestamp('get_user_data')
    user = anvil.users.get_user(allow_remembered=True)
    # TODO: first check if this same background task is running, by checking the users table.
    return anvil.server.launch_background_task('get_user_data_bk', user)


@anvil.server.background_task
def get_user_data_bk(user):
    print_timestamp('get_user_data_bk: start')
    usermap = _get_usermap(user)
    permissions = _get_permissions(user, usermap)
    data = {'users': [], 'applicants': []}
    data['permissions'] = permissions
    if 'see_members' in permissions:
        data['users'] = _get_users(user)
    if 'see_applicants' in permissions:
        data['applicants'] = _get_applicants(user)
    print_timestamp('get_user_data_bk: end')
    return data


@anvil.server.callable(require_user=True)
def get_usermap():
    user = anvil.users.get_user(allow_remembered=True)
    if not user:
        raise ValueError('User is not logged in.')
    return _get_usermap(user)

def _get_usermap(user):
    if not app_tables.usermap.get(user=user):
        # TODO: add some defaults
        usermap = app_tables.usermap.add_row(user=user)
    else:
        usermap = app_tables.usermap.get(user=user)
    return usermap


@anvil.server.callable(require_user=True)
def get_permissions(tenant_id):
    """Get the permissions of a user in a particular tenant."""
    user = anvil.users.get_user(allow_remembered=True)
    return _get_permissions(user, tenant_id)


def _get_permissions(user, tenant_id, usermap=None):
    """Get the permissions of a user in a particular tenant."""
    usermap = usermap or app_tables.usermap.get(user=user)
    try:
        user_permissions = set(
            permission["name"]
            for role in usermap["roles"]
            for permission in role["permissions"]
            if role['tenant'].get_id() == tenant_id
        )
        return list(user_permissions)
    except TypeError:
        return []


def populate_permissions():
    """Populate the permissions table."""
    permissions = [
        'see_applicants',
        'see_members',
        'see_profile',
        'see_forum',
        'book_interview',
        'dev'
    ]
    if len(app_tables.permissions.search()) == 0:
        for perm in permissions:
            app_tables.permissions.add_row(name=perm)