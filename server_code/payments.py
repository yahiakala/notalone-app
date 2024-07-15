import anvil.server
import anvil.secrets
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.users

from .helpers import get_users_with_permission, validate_user, usermap_row_to_dict, upsert_role
from .emails import notify_paid
from .paypal import verify_webhook, create_subscription, get_subscription_id


@anvil.server.callable(require_user=True)
def create_sub(tenant_id, plan_id):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    client_id = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_client_id'])
    client_secret = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_secret'])

    return_url = anvil.server.get_app_origin() + '/#app/paymentconfirm'
    cancel_url = anvil.server.get_app_origin() + '/#app/profile'
    print(return_url)
    response = create_subscription(client_id, client_secret, plan_id, return_url, cancel_url)

    plan = [i for i in tenant['paypal_plans'] if i['id'] == plan_id][0]
    
    usermap['fee'] = plan['amt']
    usermap['paypal_sub_id'] = response['id']
    # TODO: also return usermap_row_to_dict
    membermap = usermap_row_to_dict(usermap)
    if 'see_members' not in permissions:
        membermap['notes'] = ''
    
    return membermap, response['links'][0]['href']


@anvil.server.http_endpoint('/capture-sub', methods=['POST'])
def capture_sub(**params):
    headers = anvil.server.request.headers
    print(headers)
    body = anvil.server.request.body_json
    raw_body = anvil.server.request.body.get_bytes().decode('utf-8')
    print(raw_body)

    # listen_events = ['BILLING.SUBSCRIPTION.ACTIVATED',
    #                  'BILLING.SUBSCRIPTION.EXPIRED',
    #                  'BILLING.SUBSCRIPTION.UPDATED']
    # if body['event_type'] not in listen_events:
    #     print(f"not interested in this event: {body['event_type']}")
    #     return anvil.server.HttpResponse(200)

    sub_id = get_subscription_id(body)
    usermap = app_tables.usermap.get(paypal_sub_id=sub_id)
    if not usermap:
        return anvil.server.HttpResponse(400)

    print('Found user:')
    print(usermap['user']['email'])

    client_id = anvil.secrets.decrypt_with_key('encryption_key', usermap['tenant']['paypal_client_id'])
    client_secret = anvil.secrets.decrypt_with_key('encryption_key', usermap['tenant']['paypal_secret'])
    webhook_id = anvil.secrets.decrypt_with_key('encryption_key', usermap['tenant']['paypal_webhook_id'])
    
    if not verify_webhook(client_id, client_secret, webhook_id, headers, body):    
        print('Webhook not verified.')
        return anvil.server.HttpResponse(400)
    print('Webhook verified.')
    
    anvil.server.launch_background_task('update_subscription', usermap, headers, body)
    return anvil.server.HttpResponse(200)


@anvil.server.background_task
def update_subscription(usermap, headers, body):
    plan_id = body['resource']['plan_id']
    
    plan = [i for i in usermap['tenant']['paypal_plans'] if i['id'] == plan_id][0]

    if body['resource']['status'] == 'EXPIRED':
        for role in plan['roles']:
            usermap['roles'] = [i for i in usermap['roles'] if i['name'] != role]
            usermap = upsert_role(usermap, 'Approved')
    elif body['resource']['status'] == 'ACTIVE':
        for role in plan['roles']:
            usermap = upsert_role(usermap, role)
            usermap['roles'] = [i for i in usermap['roles'] if i['name'] not in ['Applicant', 'Approved']]
        notify_admins(usermap)

    usermap['payment_status'] = body['resource']['status']
    usermap['fee'] = float(body['resource']['billing_info']['last_payment']['amount']['value'])


def notify_admins(usermap):
    screeners = get_users_with_permission(None, 'see_members', usermap['tenant'])
    for screener in screeners:
        print('Sending email to : ' + screener['user']['email'])
        notify_paid(screener, usermap)


def calc_rev12():
    for tenant in app_tables.tenants.search():
        tenantfin = app_tables.finances.get(tenant=tenant)
        total_rev = 0
        for user_ref in app_tables.users.search(tenant=tenant, fee=q.not_(None), good_standing=True):
            total_rev += user_ref['fee']*0.97-0.3
        tenantfin['rev_12'] = total_rev
        total_rev = 0
        for user_ref in app_tables.users.search(tenant=tenant, fee=q.not_(None), good_standing=True, payment_status='ACTIVE'):
            total_rev += user_ref['fee']*0.97-0.3
        tenantfin['rev_12_active'] = total_rev
