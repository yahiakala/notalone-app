"""Temp stuff for migration"""
from anvil.tables import app_tables
import anvil.tables.query as q


def migrate_tables():
    users = app_tables.users.search(tenant=q.not_(None))
    for user in users:
        usermap = app_tables.usermap.get(user=user)
        if not usermap:
            usermap = app_tables.usermap.add_row(user=user)
        if user['tenant'] and not usermap['tenants']:
            usermap['tenants'] = [user['tenant']]
        usermap['roles'] = user['roles']


def tenants_to_tenant():
    users = app_tables.users.search(tenant=q.not_(None))
    for user in users:
        usermap = app_tables.usermap.get(user=user)
        if not usermap:
            usermap = app_tables.usermap.add_row(user=user)
        for key in ['tenant', 'fee', 'paypal_sub_id', 'consent_check', 'booking_link',
                    'payment_expiry', 'payment_status', 'discord', 'phone', 'screening_slots']:
            usermap[key] = user[key]
        note = app_tables.notes.get(user=user, tenant=user['tenant'])
        if note:
            usermap['notes'] = note['notes']

def migrate_roles():
    users = app_tables.users.search(tenant=q.not_(None))
    for user in users:
        usermap = app_tables.usermap.get(user=user, tenant=user['tenant'])
        if not usermap:
            usermap = app_tables.usermap.add_row(user=user, tenant=user['tenant'])
            
        if user['auth_members']:
            upsert_role(usermap, 'Admin')
        elif user['auth_screenings']:
            upsert_role(usermap, 'Interviewer')
        elif user['auth_forumchat']:
            upsert_role(usermap, 'Member')
        elif user['auth_profile']:
            upsert_role(usermap, 'Approved')
        elif user['auth_booking']:
            upsert_role(usermap, 'Applicant')
        else:
            usermap['roles'] = None


def upsert_role(usermap, role_name):
    role = app_tables.roles.get(tenant=usermap['tenant'], name=role_name)
    if not usermap['roles']:
        usermap['roles'] = [role]
    elif role not in usermap['roles']:
        usermap['roles'] = usermap['roles'] + [role]


def migrate_firstlast():
    users = app_tables.users.search(tenant=q.not_(None))
    for user in users:
        usermap = app_tables.usermap.get(user=user, tenant=user['tenant'])
        if not usermap:
            usermap = app_tables.usermap.add_row(user=user, tenant=user['tenant'])

        usermap['first_name'] = user['first_name']
        usermap['last_name'] = user['last_name']


def clear_tenant_data():
    tenant = app_tables.tenants.get()
    if tenant:
        usermaps = app_tables.usermap.search(tenant=tenant)
        for usermap in usermaps:
            usermap.delete()
        roles = app_tables.roles.search(tenant=tenant)
        for role in roles:
            role.delete()
        for perm in app_tables.permissions.search():
            perm.delete()
        tenant.delete()


def migrate_all():
    users = app_tables.users.search(tenant=q.not_(None))
    tenant = app_tables.tenants.get()
    
    for user in users:
        usermap = app_tables.usermap.get(user=user, tenant=tenant)
        if not usermap:
            usermap = app_tables.usermap.add_row(user=user, tenant=tenant)
        for key in ['fee', 'paypal_sub_id', 'consent_check', 'booking_link',
                    'payment_expiry', 'payment_status', 'discord', 'phone', 'screening_slots',
                    'first_name', 'last_name']:
            usermap[key] = user[key]
        
        note = app_tables.notes.get(user=user, tenant=tenant)
        if note:
            usermap['notes'] = note['notes']

        if user['auth_members']:
            upsert_role(usermap, 'Admin')
        elif user['auth_screenings']:
            upsert_role(usermap, 'Interviewer')
        elif user['auth_forumchat']:
            upsert_role(usermap, 'Member')
        elif user['auth_profile']:
            upsert_role(usermap, 'Approved')
        elif user['auth_booking']:
            upsert_role(usermap, 'Applicant')
        else:
            usermap['roles'] = None