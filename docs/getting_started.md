# Getting Started Guide

This guide will help you set up your development environment for contributing to the Not Alone app. The app is built using Anvil's web framework and integrates with several external services.

## Prerequisites

Before starting, ensure you have:
- A GitHub account
- A PayPal developer account
- A DigitalOcean account (for Discourse hosting)
- Basic knowledge of Python and web development

## 1. Fork and Clone Repositories

### Main Application Repository

1. Fork the Not Alone repository:
   ```bash
   # Visit https://github.com/yahiakala/notalone-app
   # Click "Fork" button
   ```

2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/notalone-app.git
   cd notalone-app
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/yahiakala/notalone-app.git
   ```

## 2. Anvil Setup

### Create Free Account

1. Visit [anvil.works](https://anvil.works)
2. Sign up for a free account
3. Choose the "Free" plan (sufficient for development)

### Clone the App

1. In Anvil dashboard, click "New App"
2. Choose "Clone from GitHub"
3. Enter your forked repository URL
4. Select "Material Design Theme"

### Local Development Setup

1. Install Anvil CLI:
   ```bash
   pip install anvil-app-server
   ```

2. Configure local server:
   ```bash
   anvil-app-server --app notalone-app
   ```

## 3. Discourse Setup

### DigitalOcean Deployment

1. Create DigitalOcean account
2. From Marketplace, select "Discourse"
3. Choose a plan:
   - Basic droplet ($5/month sufficient for development)
   - Any region
   - Add SSH key for secure access

4. Configure domain/subdomain:
   ```
   discourse.yourdomain.com
   ```

### Discourse Configuration

1. Access admin panel:
   ```
   https://discourse.yourdomain.com/admin
   ```

2. Generate API credentials:
   - Navigate to API settings
   - Create new API key
   - Note down:
     - API Key
     - API Username
     - API URL

3. Configure webhook settings:
   ```json
   {
     "discourse_url": "https://discourse.yourdomain.com",
     "discourse_api_key": "your_api_key",
     "discourse_username": "system"
   }
   ```

## 4. PayPal Integration

### Developer Account Setup

1. Create PayPal developer account:
   - Visit [developer.paypal.com](https://developer.paypal.com)
   - Sign up for developer account

2. Create sandbox accounts:
   - Create business account
   - Create personal account for testing

### API Configuration

1. Create app in PayPal:
   ```
   My Apps & Credentials > Create App
   ```

2. Note credentials:
   - Client ID
   - Client Secret

3. Create subscription plan:
   ```
   Products > Create Product > Create Plan
   ```

### Webhook Setup

1. Configure webhook URL:
   ```
   https://your-anvil-app.anvil.app/_/api/capture-sub
   ```

2. Subscribe to events:
   - BILLING.SUBSCRIPTION.ACTIVATED
   - BILLING.SUBSCRIPTION.CANCELLED
   - BILLING.SUBSCRIPTION.EXPIRED
   - BILLING.SUBSCRIPTION.UPDATED

## 5. Development Environment Configuration

### Environment Variables

Create a `.env` file in your project root:
```bash
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_SECRET=your_client_secret
DISCOURSE_API_KEY=your_api_key
DISCOURSE_URL=your_discourse_url
```

### Database Setup

The app uses Anvil's built-in database. Create required tables:

1. Users table
2. Usermap table
3. Tenants table
4. Roles table
5. Permissions table
6. Files table
7. RoleFiles table
8. Notes table
9. Forum table
10. Finances table

Refer to `docs/schema.md` for detailed table structures.

## 6. Running the Application

### Start Local Server

1. Run Anvil server:
   ```bash
   anvil-app-server --app notalone-app
   ```

2. Access local app:
   ```
   http://localhost:3030
   ```

### Development Workflow

1. Create feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and test locally

3. Commit changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create pull request on GitHub

## 7. Testing

### PayPal Testing

1. Use sandbox accounts for testing payments
2. Test subscription flows:
   - Creation
   - Cancellation
   - Updates
   - Webhook processing

### Discourse Testing

1. Create test categories and topics
2. Test API integration:
   - User creation
   - Post creation
   - Category management

## 8. Common Issues and Solutions

### Anvil Connection Issues

If you encounter connection issues:
1. Check Anvil server status
2. Verify uplink key configuration
3. Check network connectivity

### PayPal Webhook Issues

If webhooks aren't received:
1. Verify webhook URL is accessible
2. Check webhook signature verification
3. Validate event types in PayPal dashboard

### Discourse API Issues

If Discourse integration fails:
1. Verify API credentials
2. Check API endpoint URLs
3. Confirm API user permissions

## 9. Contributing Guidelines

1. Follow existing code style
2. Add tests for new features
3. Update documentation
4. Create detailed pull request descriptions

## 10. Additional Resources

- [Anvil Documentation](https://anvil.works/docs)
- [PayPal Developer Docs](https://developer.paypal.com/docs)
- [Discourse API Guide](https://docs.discourse.org)
- Project-specific docs in `/docs` directory

## Support

For development support:
1. Check existing documentation
2. Search GitHub issues
3. Create new issue if needed
4. Join development discussions

Remember to always work in your own fork and create pull requests for changes you want to contribute to the main project.
