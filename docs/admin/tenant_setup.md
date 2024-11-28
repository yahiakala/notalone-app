# Tenant Setup Guide

This guide walks you through setting up a new tenant in the Not Alone app, including PayPal integration, webhook configuration, and admin settings.

## Initial Setup

### 1. Basic Information

After logging in as a tenant admin, navigate to the Admin screen (`#app/admin`) and configure:

![Admin screen overview showing main configuration options](images/admin_1.png)

1. Organization Details:
   - Organization name
   - Contact email
   - Upload organization logo
   - Set waiver/terms document URL

![PayPal integration settings showing API credentials and subscription configuration](images/admin_2.png)

2. Integration Settings:
   - Discourse forum URL
   - Discourse Connect secret (for authenticating users)
   - Discourse API key (for automations)
   - PayPal Client ID and Secret
   - Payment webhook ID

![Discourse forum integration settings including API keys and SSO configuration](images/admin_3.png)

3. PayPal Plan Settings
    - Enter your PayPal plan information
    - Enter Plan Name, Plan ID (from PayPal), frequency, etc.
    - Assign roles to members who pay through this subscription.

4. Discord invite link (optional)

### 2. Role Configuration

Set up roles for your organization:

![Roles overview screen](images/roles_0.png)

1. Navigate to Roles section
2. Some basic roles are already defined and not editable. To create custom roles, see below.

![Role creation and configuration](images/roles_1.png)

3. For each role, configure:
   - Role name
   - Associated permissions
   - Upload role guide document (if applicable)

![Role permissions and document management](images/roles_2.png)

By clicking on 'Details' in the Roles screen, you can see which permissions belong to each role.
You can also see (end edit) which files are attached for each role. These files serve as guides.

Configure permissions for different roles:

1. Basic Permissions:
   - `see_members`: View member list
   - `edit_members`: Modify member details
   - `see_forum`: Access community forum
   - `see_financials`: View financial reports

2. Administrative Permissions:
   - `delete_admin`: Full administrative access
   - `delete_members`: Ability to delete members


![Role detail](images/role_detail.png)

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
     - PAYMENT.SALE.COMPLETED

3. Note the:
   - Webhook ID
