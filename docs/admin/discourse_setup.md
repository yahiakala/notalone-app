# Discourse Setup

### Mailjet Instructions

1. Go to Mailjet and get an SMTP setting for your forum
   - For detailed instructions on setting up Mailjet SMTP, including SPF and DKIM configuration, see our [Mailjet Setup Guide](mailjet_setup.md)

### DigitalOcean Deployment

Watch this video if you want to see a tutorial on how to install discourse:

<iframe width="560" height="315" src="https://www.youtube.com/embed/sjFlBgSiyCY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

1. Create DigitalOcean account
2. From Marketplace, select "Discourse"
3. Choose a plan:
    - Basic droplet
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

3. Configure SSO Settings:
    - Enable invite only: All new users must be explicitly invited by trusted users or staff
    - Enable login required: Require authentication to read content, disallow anonymous access
    - Enable local logins: Allow username and password login based accounts
    - Enable local login via email: Allow users to request one-click login links via email
    - Enable persistent sessions: Users will remain logged in when the web browser is closed
    - Set maximum session age: 12 hours since last visit
    - Enable DiscourseConnect (formerly 'Discourse SSO'): This must be enabled for SSO integration
    - Configure DiscourseConnect URL: Set to your application's SSO endpoint (e.g., https://your-app-url/_/api/discourse-sso)
    - Set DiscourseConnect secret: Create a secure secret string (minimum 10 characters)
    - Enable verbose DiscourseConnect logging: Log detailed SSO diagnostics to /logs
    - Enable auth overrides email: Override local email with external site email on every login
    - Do not enable:
        - Must approve users
        - Auth overrides username
        - Auth overrides name
        - Discourse connect overrides groups
        - Discourse connect overrides bio
        - Discourse connect overrides avatar
        - Discourse connect overrides profile background
        - Hide email address taken
        - Log out strict

4. Configure the API settings by going to Admin > API
    - Create an API key, save it for entering it in your Anvil app's tenant settings later.
    - Create a webhook that points to https://your-app-url/_/api/new_member.
        - Give it a secret that you remember for later
        - Select the 'user is created' event
        - Scroll to the bottom of the page and check 'Check TLS...' and 'Active'
        - Hit 'Save'.
