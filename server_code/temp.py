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