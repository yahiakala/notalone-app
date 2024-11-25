# Payment System Documentation

## Overview

The Not Alone app implements a multi-tenant payment system using PayPal subscriptions. Each tenant can configure their own PayPal integration and subscription plans, which their members can then subscribe to.

## Important PayPal Webhook Limitations

**Note:** PayPal does not generate webhook events for merchant-initiated subscription cancellations (cancellations done through PayPal's interface). While subscriber-initiated cancellations trigger the BILLING.SUBSCRIPTION.CANCELLED webhook properly, cancellations done by merchants through PayPal's dashboard do not generate any webhook events. To handle this limitation, the app implements a periodic subscription status check.

## Development and Testing Requirements

**Important:** For test deployments, the deployment URL **must** contain either 'debug' or 'test' in the URL (e.g., 'https://debug-myapp.anvil.app' or 'https://test-myapp.anvil.app'). This is required for the app to automatically use PayPal's sandbox APIs instead of production APIs. If the URL does not contain 'debug' or 'test', the app will use production PayPal APIs.

## Tenant Configuration

### PayPal Integration Setup

Each tenant requires the following PayPal configuration in the `tenants` table:
- `paypal_client_id`: PayPal API client ID
- `paypal_secret`: PayPal API secret
- `paypal_plans`: JSON object containing subscription plan configurations
- `paypal_webhook_id`: PayPal webhook identifier for subscription notifications
- `paypal_webhook_certificate`: PayPal webhook certificate for verification

### Subscription Plans

Plans are configured in the `paypal_plans` field of the tenants table as a JSON object:

```json
{
  "id": "PLAN_ID",
  "amt": 25.00,
  "roles": ["Member"],
  "name": "Monthly Membership",
  "description": "Regular monthly membership subscription"
}
```

Each plan specifies:
- PayPal plan ID
- Amount to charge
- Roles to assign upon successful subscription
- Plan name and description

## Payment Flow

### 1. Subscription Creation

When a user initiates a subscription:

```python
@anvil.server.callable(require_user=True)
def create_sub(tenant_id, plan_id):
    # Validate user and tenant
    tenant, usermap, permissions = validate_user(tenant_id, user)

    # Get PayPal credentials
    client_id = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_client_id'])
    client_secret = anvil.secrets.decrypt_with_key('encryption_key', tenant['paypal_secret'])

    # Create subscription
    response = create_subscription(client_id, client_secret, plan_id, return_url, cancel_url)

    # Update user record
    usermap['fee'] = plan['amt']
    usermap['paypal_sub_id'] = response['id']
```

### 2. PayPal Redirect

The user is redirected to PayPal to complete the subscription:

```python
def pay_click(self, item, **event_args):
    self.member, self.payment_url = anvil.server.call("create_sub", Global.tenant_id, item['id'])
    window.location.href = self.payment_url
```

### 3. Webhook Processing

PayPal webhooks notify the application of subscription status changes:

```python
@anvil.server.http_endpoint('/capture-sub', methods=['POST'])
def capture_sub(**params):
    # Verify webhook authenticity
    if not verify_webhook(client_id, client_secret, webhook_id, headers, body):
        return anvil.server.HttpResponse(400)

    # Process subscription update in background
    anvil.server.launch_background_task('update_subscription', usermap, headers, body)
```

### 4. Subscription Updates

Background task processes subscription status changes:

```python
@anvil.server.background_task
def update_subscription(usermap, headers, body):
    # Update roles based on subscription status
    if body['resource']['status'] == 'EXPIRED':
        remove_subscription_roles(usermap, plan)
    elif body['resource']['status'] == 'ACTIVE':
        add_subscription_roles(usermap, plan)

    # Update payment status and fee
    usermap['payment_status'] = body['resource']['status']
    usermap['fee'] = get_subscription_amount(body)
```

## Client-Side Implementation

### Member Detail View

The MemberDetail component handles payment UI:

1. Displays current subscription status:
```python
if 'see_forum' in self.member['permissions']:
    self.cp_payment_status.visible = True
    if self.member['payment_status'] == 'CANCELLED':
        self.lbl_fee_paid_copy.text = "Subscription cancelled but membership still in good standing."
```

2. Shows subscription cancellation option:
```python
if self.member['paypal_sub_id']:
    self.btn_cancel_sub.visible = True
```

3. Displays pricing plans for new subscriptions:
```python
if 'see_forum' not in self.member['permissions']:
    for plan in Global.tenant['paypal_plans']:
        self.fp_pricing_table.add_component(PriceCard(item=plan))
```

## Server-Side Implementation

### PayPal API Integration

The `paypal.py` module handles PayPal API interactions:

1. Authentication:
```python
def get_paypal_auth(client_id, client_secret):
    auth_response = anvil.http.request(
        TOKEN_URL,
        method="POST",
        username=client_id,
        password=client_secret,
        data={'grant_type': 'client_credentials'}
    )
    return auth_response['access_token']
```

2. Subscription Management:
```python
def create_subscription(client_id, client_secret, plan_id, return_url, cancel_url):
    access_token = get_paypal_auth(client_id, client_secret)
    return anvil.http.request(
        SUBSCRIPTION_URL,
        method='POST',
        headers={'Authorization': f'Bearer {access_token}'},
        data={'plan_id': plan_id, 'application_context': {...}}
    )
```

3. Webhook Verification:
```python
def verify_webhook(client_id, client_secret, webhook_id, headers, body):
    access_token = get_paypal_auth(client_id, client_secret)
    response = anvil.http.request(
        VERIFY_URL,
        headers={'Authorization': f'Bearer {access_token}'},
        data={'webhook_id': webhook_id, 'webhook_event': body, ...}
    )
    return response['verification_status'] == 'SUCCESS'
```

## Revenue Tracking

The system tracks revenue through the `finances` table:

```python
def calc_rev12():
    for tenant in app_tables.tenants.search():
        tenantfin = app_tables.finances.get(tenant=tenant)
        # Calculate total revenue (including PayPal fees)
        total_rev = sum((user['fee'] * 0.97 - 0.3)
                       for user in active_paying_users(tenant))
        tenantfin['rev_12'] = total_rev
```

## Best Practices

1. **Secure Credential Storage**
   - Store PayPal credentials encrypted in the tenant table
   - Use `anvil.secrets.decrypt_with_key()` to access credentials

2. **Webhook Security**
   - Always verify webhook authenticity before processing
   - Use background tasks for webhook processing to prevent timeouts
   - Be aware that merchant-initiated cancellations won't trigger webhooks

3. **Error Handling**
   - Implement proper error handling for PayPal API calls
   - Provide clear feedback to users on payment failures

4. **Subscription Management**
   - Keep subscription IDs and status in sync with PayPal
   - Update user roles immediately upon subscription changes
   - Run periodic status checks to catch merchant-initiated cancellations

5. **Revenue Calculations**
   - Account for PayPal fees in revenue calculations
   - Track both total and active subscription revenue
