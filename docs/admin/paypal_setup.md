# PayPal Setup Guide

This guide covers setting up PayPal for both testing (sandbox) and production environments, specifically for subscription payments and webhooks.

## Sandbox Environment Setup

### 1. Create Developer Accounts

1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/)
2. Create two sandbox accounts:
    - Business account (to receive payments)
    - Personal account (to make test payments)

### 2. Create Sandbox App

1. In Developer Dashboard, go to "Apps & Credentials"
2. Click "Create App"
3. Select "Sandbox" for testing environment
4. Name your application (e.g., "Not Alone Test")
5. Note down:
    - Client ID
    - Client Secret

### 3. Create Subscription Plans

1. Navigate to "Products & Plans"
2. Create a product:
   ```
   Products > Create Product
   ```
3. Create subscription plan(s):
    - Set billing cycle (use daily for testing)
    - Set price points
    - Note down Plan ID for each plan

### 4. Configure Webhooks

1. Go to "Webhooks" in Developer Dashboard
2. Click "Add Webhook"
3. Enter your webhook URL:
   ```
   https://your-app-url/_/api/capture-sub
   ```
4. Subscribe to these events:
    - BILLING.SUBSCRIPTION.ACTIVATED
    - BILLING.SUBSCRIPTION.CANCELLED
    - BILLING.SUBSCRIPTION.EXPIRED
    - BILLING.SUBSCRIPTION.UPDATED
    - PAYMENT.SALE.COMPLETED
5. Save and note down the Webhook ID

## Production Environment Setup

### 1. Business Account Setup

1. Create or use existing [PayPal Business account](https://www.paypal.com/business)
2. Ensure your business account is verified and in good standing

### 2. Create Live App

1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/)
2. Click "Create App"
3. Select "Live" for production environment
4. Name your application (e.g., "Not Alone")
5. Note down:
    - Client ID
    - Client Secret

### 3. Create Live Subscription Plans

1. Navigate to "Products & Plans"
2. Create your product:
   ```
   Products > Create Product
   ```
3. Create subscription plan(s):
    - Set actual billing cycle (monthly/yearly)
    - Set real price points
    - Note down Plan ID for each plan

### 4. Configure Live Webhooks

1. Go to "Webhooks" in Developer Dashboard
2. Click "Add Webhook"
3. Enter your production webhook URL:
   ```
   https://your-production-url/_/api/capture-sub
   ```
4. Subscribe to these events:
    - BILLING.SUBSCRIPTION.ACTIVATED
    - BILLING.SUBSCRIPTION.CANCELLED
    - BILLING.SUBSCRIPTION.EXPIRED
    - BILLING.SUBSCRIPTION.UPDATED
    - PAYMENT.SALE.COMPLETED
5. Save and note down the Webhook ID

## Testing

### Sandbox Testing Checklist

1. Test subscription creation:
    - Use sandbox personal account to subscribe
    - Verify webhook notification
    - Check subscription status in business account

2. Test subscription cancellation:
    - Cancel subscription from personal account
    - Verify webhook notification
    - Check status update in business account

3. Test subscription updates:
    - Modify subscription if your plans allow it
    - Verify webhook notification
    - Confirm changes in both accounts

4. Test recurring payment processing:
    - Confirm successful payment capture
    - Verify PAYMENT.SALE.COMPLETED webhook
    - Check payment appears in business account

### Production Verification

Before going live:

1. Verify all webhook endpoints are correctly configured
2. Test a small real transaction
3. Confirm subscription plans are correctly priced
4. Verify all PayPal buttons are using production credentials
