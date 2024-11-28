# Tenant Setup Guide

This guide walks you through setting up a new tenant in the Not Alone app, including PayPal integration, webhook configuration, and admin settings.

## Initial Setup

### 1. Basic Information

After logging in as a tenant admin, navigate to the Admin screen (`#app/admin`) and configure:

1. Organization Details:
   - Organization name
   - Contact email
   - Upload organization logo
   - Set waiver/terms document URL

2. Communication Settings:
   - SMTP email for notifications
   - Discord invite link (if using Discord)

### 2. Role Configuration

Set up roles for your organization:

1. Navigate to Roles section
2. Create basic roles:
   - Member (default paid member role)
   - Admin (administrative access)
   - Volunteer (if applicable)

3. For each role, configure:
   - Role name
   - Reporting structure
   - Associated permissions
   - Upload role guide document (if applicable)

## PayPal Integration

### 1. PayPal Business Account Setup

Before configuring in Not Alone:

1. Create a PayPal Business account if you don't have one
2. Navigate to PayPal Developer Dashboard
3. Create a new app to get API credentials:
   - Client ID
   - Client Secret

### 2. Create Subscription Plans

In PayPal Developer Dashboard:

1. Create subscription plans:
   ```
   Products > Create Product > Create Plan
   ```

2. For each plan, note:
   - Plan ID
   - Pricing details
   - Billing cycle

### 3. Configure in Not Alone

In the Admin screen, PayPal section:

1. Enter API Credentials:
   - PayPal Client ID
   - PayPal Secret

2. Configure Plans:
   ```json
   {
     "id": "PLAN_ID_FROM_PAYPAL",
     "amt": 25.00,
     "roles": ["Member"],
     "name": "Monthly Membership",
     "description": "Regular monthly membership"
   }
   ```

   You can configure multiple plans with different:
   - Amounts
   - Roles assigned
   - Billing frequencies

## Webhook Configuration

### 1. Create PayPal Webhook

In PayPal Developer Dashboard:

1. Navigate to Webhooks section
2. Create new webhook:
   - URL: `https://your-app-url/capture-sub`
   - Events to track:
     - BILLING.SUBSCRIPTION.ACTIVATED
     - BILLING.SUBSCRIPTION.CANCELLED
     - BILLING.SUBSCRIPTION.EXPIRED
     - BILLING.SUBSCRIPTION.UPDATED

3. Note the:
   - Webhook ID
   - Webhook signing certificate

### 2. Configure in Not Alone

In Admin screen, Webhook section:

1. Enter webhook details:
   - Webhook ID
   - Webhook certificate

2. Test webhook:
   - Use PayPal's webhook simulator
   - Verify events are received

## Admin Settings

### 1. Permission Configuration

Configure permissions for different roles:

1. Basic Permissions:
   - `see_members`: View member list
   - `edit_members`: Modify member details
   - `see_forum`: Access community forum
   - `see_financials`: View financial reports

2. Administrative Permissions:
   - `delete_admin`: Full administrative access
   - `auth_dev`: Developer access
   - `auth_booking`: Booking system access

### 2. Financial Settings

Set up financial tracking:

1. Configure budgets in the Finance section
2. Set up revenue tracking
3. Configure financial reports

### 3. Integration Settings

If using forum integration:

1. Discourse Settings:
   - API Key
   - API Secret
   - Forum URL

2. Discord Settings:
   - Server invite link
   - Integration settings

## Verification Steps

After configuration, verify:

1. Member Signup Flow:
   - Test member registration
   - Verify PayPal subscription creation
   - Check role assignment

2. Payment Processing:
   - Create test subscription
   - Verify webhook notifications
   - Check member status updates

3. Administrative Functions:
   - Test member management
   - Verify report generation
   - Check financial calculations

## Best Practices

1. **Security**
   - Regularly rotate API keys
   - Use strong passwords
   - Monitor access logs

2. **Member Management**
   - Set clear role hierarchies
   - Document permission assignments
   - Maintain role guides

3. **Financial Tracking**
   - Regular revenue reconciliation
   - Monitor subscription status
   - Track payment failures

4. **Communication**
   - Set up email templates
   - Configure notification settings
   - Test communication flows

## Troubleshooting

Common issues and solutions:

1. **Webhook Failures**
   - Verify webhook URL is accessible
   - Check webhook signature verification
   - Validate event types

2. **Payment Issues**
   - Verify PayPal credentials
   - Check plan IDs match
   - Validate webhook processing

3. **Role Assignment**
   - Verify permission configuration
   - Check role hierarchy
   - Validate automatic assignments

## Support

For additional support:

1. Contact system administrators
2. Check documentation updates
3. Review error logs in admin panel
