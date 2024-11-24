import anvil.server
import anvil.secrets
from anvil.tables import app_tables
import anvil.tables.query as q
import anvil.users

from .helpers import get_users_with_permission, validate_user, usermap_row_to_dict, upsert_role
from .emails import notify_paid
from .paypal import verify_webhook, create_subscription, get_subscription_id, cancel_subscription


@anvil.server.callable(require_user=True)
def create_sub(tenant_id, plan_id):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    client_id = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_client_id'])
    client_secret = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_secret'])

    # TODO: add tenant id to the return urls and route the app properly
    return_url = anvil.server.get_app_origin() + '/payment-success'
    cancel_url = anvil.server.get_app_origin() + '/payment-cancel'
    # print(return_url)
    # print(cancel_url)
    # return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#profile'})
    response = create_subscription(client_id, client_secret, plan_id, return_url, cancel_url)

    plan = [i for i in tenant['paypal_plans'] if i['id'] == plan_id][0]
    
    usermap['fee'] = plan['amt']
    usermap['paypal_sub_id'] = response['id']
    # TODO: also return usermap_row_to_dict
    membermap = usermap_row_to_dict(usermap)
    if 'see_members' not in permissions:
        membermap['notes'] = ''
    
    return membermap, response['links'][0]['href']


@anvil.server.callable(require_user=True)
def cancel_user_subscription(tenant_id, email):
    """Cancel a user's PayPal subscription."""
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    
    # Check if user has permission to cancel subscription
    if email != user['email'] and 'edit_members' not in permissions:
        raise Exception("You don't have permission to cancel other users' subscriptions")
    
    # Get the target user and validate
    target_user = app_tables.users.get(email=email)
    if not target_user:
        raise Exception("User not found")
    
    # Get the membermap for the target user
    _, membermap, _ = validate_user(tenant_id, target_user)
    if not membermap or not membermap['paypal_sub_id']:
        raise Exception("No active subscription found")
    
    client_id = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_client_id'])
    client_secret = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_secret'])
    
    # Cancel the subscription with PayPal
    cancel_subscription(client_id, client_secret, membermap['paypal_sub_id'])
    
    # Update user's subscription status
    membermap['payment_status'] = 'CANCELLED'
    
    result_membermap = usermap_row_to_dict(membermap)
    if 'see_members' not in permissions:
        result_membermap['notes'] = ''
    
    return result_membermap


@anvil.server.route('/payment-success')
def payment_success(**kwargs):
    return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#app/paymentconfirm'})


@anvil.server.route('/payment-cancel')
def payment_cancel(**kwargs):
    return anvil.server.HttpResponse(302, headers={'Location': anvil.server.get_app_origin() + '/#app/profile'})


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

    # print(client_id)
    # print(client_secret)
    # print(webhook_id)
    
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
            # TODO: Test more.
            usermap = upsert_role(usermap, 'Approved')
            usermap['roles'] = [i for i in usermap['roles'] if i['name'] != role]
    elif body['resource']['status'] == 'ACTIVE':
        for role in plan['roles']:
            usermap = upsert_role(usermap, role)
            # only add role if they are approved
            approved_role = app_tables.roles.get(name='Approved', tenant=usermap['tenant'])
            if approved_role in usermap['roles']:
                usermap['roles'] = [i for i in usermap['roles'] if i['name'] not in ['Applicant', 'Approved']]
        notify_admins(usermap)

    usermap['payment_status'] = body['resource']['status']
    if 'billing_info' in body['resource']:
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
