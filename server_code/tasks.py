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
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        return app_tables.tenants.client_readable(q.only_cols('name'))
    else:
        return []


@anvil.server.callable(require_user=True)
def join_tenant(id):
    user = anvil.users.get_user(allow_remembered=True)
    if user['tenant'] is None:
        user['tenant'] = app_tables.tenants.get_by_id(id)
        # Now let the user book an interview
        user['auth_booking'] = True
    return user


@anvil.server.callable(require_user=True)
def leave_tenant():
    # TODO: what is this used for?
    user = anvil.users.get_user(allow_remembered=True)
    for key, val in user.items():
        if 'auth_' in key and 'auth_dev' not in key:
            user[key] = False
    user['tenant'] = None
    return user


@anvil.server.callable(require_user=True)
def update_user(user_dict):
    user = anvil.users.get_user(allow_remembered=True)
    for key in ['first_name', 'last_name', 'fb_url', 'fee', 'consent_check', 'paypal_sub_id', 'phone', 'discord']:
        if user[key] != user_dict[key]:
            user[key] = user_dict[key]
    user = clean_up_user(user)
    return user


@permission_required('auth_members')
def update_user_admin(email, col_name, col_value):
    doer = anvil.users.get_user(allow_remembered=True)
    user = app_tables.users.get(tenant=doer['tenant'], email=email)
    user[col_name] = col_value


@permission_required('auth_members')
def delete_user(user_dict):
    user_del = app_tables.users.get(email=user_dict['email'], auth_members=q.not_(True))
    user_del.delete()


@permission_required('auth_members')
def get_users():
    """Get a full list of the users."""
    print_timestamp('get_users')
    user = anvil.users.get_user(allow_remembered=True)
    memberlist = [
        {
            'first_name': member['first_name'],
            'last_name': member['last_name'],
            'email': member['email'],
            'fb_url': member['fb_url'],
            'discord': member['discord'],
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


@permission_required('auth_members')
def user_search(search_txt):
    print_timestamp('user_search: ' + search_txt)
    user = anvil.users.get_user(allow_remembered=True)
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
    # users_list = [
    #     {
    #         'first_name': member['first_name'],
    #         'last_name': member['last_name'],
    #         'email': member['email'],
    #         'fb_url': member['fb_url'],
    #         'discord': member['discord'],
    #         'fee': member['fee'],
    #         'good_standing': member['good_standing'],
    #         'last_login': member['last_login'],
    #         'signed_up': member['signed_up'],
    #         'paypal_sub_id': member['paypal_sub_id'],
    #         'auth_screenings': member['auth_screenings'],
    #         'auth_forumchat': member['auth_forumchat'],
    #         'auth_profile': member['auth_profile'],
    #         'auth_booking': member['auth_booking'],
    #         'auth_members': member['auth_members'],
    #         'auth_dev': member['auth_dev']
    #     }
    #     for member in users
    # ]
    print_timestamp('user_search: ' + search_txt + ' done')
    return users


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
    """Get restricted, client readable view of applicants."""
    print_timestamp('get_applicants')
    user = anvil.users.get_user(allow_remembered=True)
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
            'first_name': i['first_name'],
            'last_name': i['last_name'],
            'auth_profile': i['auth_profile'],
            'auth_forumchat': i['auth_forumchat'],
            'auth_booking': i['auth_booking'],
            'good_standing': i['good_standing'],
            'signed_up': i['signed_up']
        }
        for i in app_q
    ]
    return app_list


@permission_required('auth_screenings')
def reassign_roles(user_dict, role_dict):
    """Reset roles for a user. This is for screeners to use."""
    user = anvil.users.get_user(allow_remembered=True)
    user_ref = app_tables.users.get(email=user_dict['email'], tenant=user['tenant'])
    for col_name, val in role_dict.items():
        if col_name in ['auth_profile', 'auth_forumchat', 'auth_booking']:
            user_ref[col_name] = val
    return user_ref


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
    return app_tables.finances.client_writable(tenant=user['tenant']).get()


@permission_required('auth_forumchat')
def get_forumlink():
    """Get financial info."""
    user = anvil.users.get_user(allow_remembered=True)
    return 'https://' + app_tables.forum.get(tenant=user['tenant'])['discourse_url']


@permission_required('auth_screenings')
def notify_accept(email_to):
    """Notify the applicant they've been accepted."""
    msg_body = """
    <p>Hi! This is an automated message from the NotAlone community platform.</p>
    
    <p>You have passed the screening interview!</p>

    <p>Please log into the app for next steps. Fill out your profile, read the community guidelines, and make the membership payment.</p>

    <p>Regards,</p>
    <p>NotAlone team.</p>
    """
    user = anvil.users.get_user(allow_remembered=True)
    anvil.email.send(
        to=email_to,
        bcc=user['email'],
        from_address="admin",
        from_name="NotAlone",
        subject="Welcome to the NotAlone Community!",
        html=msg_body
    )


@permission_required('auth_forumchat')
def get_roles():
    user = anvil.users.get_user(allow_remembered=True)
    return app_tables.roles.search(tenant=user['tenant'])


@permission_required('auth_members')
def get_roles_to_members():
    """Get a dict that maps roles to users."""
    user = anvil.users.get_user(allow_remembered=True)
    role_members = []
    users = list(app_tables.users.search(tenant=user['tenant']))
    for role in app_tables.roles.search(tenant=user['tenant']):
        role_members.append(
            {
                'name': role['name'],
                'last_update': role['last_update'],
                'reports_to': role['reports_to'],
                'member': [i for i in app_tables.users.search(tenant=user['tenant'], roles=[role])],
                'users': users
            }
        )
    return role_members

@permission_required('auth_members')
def add_role_to_member(role_name, member_email):
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
    user = anvil.users.get_user(allow_remembered=True)
    role = app_tables.roles.get(name=role_name, tenant=user['tenant'])
    role['last_update'] = dt.date.today()
    member = app_tables.users.get(tenant=user['tenant'], email=member_email)
    member['roles'] = [i for i in member['roles'] if i != role]


@permission_required('auth_members')
def add_role(role_name, reports_to, role_members):
    user = anvil.users.get_user(allow_remembered=True)
    if not app_tables.roles.get(tenant=user['tenant'], name=role_name):
        app_tables.roles.add_row(name=role_name, reports_to=reports_to, tenant=user['tenant'], last_update=dt.date.today())
    role_members.append(
        {
            'name': role_name,
            'last_update': dt.date.today(),
            'reports_to': reports_to,
            'member': [],
            'users': role_members[-1]['users']
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
def super_load():
    user = anvil.users.get_user(allow_remembered=True)
    data = {'members': None, 'applicants': None}
    if user['auth_members']:
        data['users'] = get_users()
    if user['auth_screenings'] or user['auth_members']:
        data['applicants'] = get_applicants()
    return data