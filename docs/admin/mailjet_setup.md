# Mailjet SMTP Setup Guide

This guide covers how to set up Mailjet as your SMTP provider for sending emails from your application.

## Important Note

Do not use Mailjet subaccounts as they have limitations and can cause issues with email deliverability. Always use the main account for better control and monitoring.

## Domain Setup

1. Choose a subdomain for sending emails
   - Create a dedicated subdomain for sending emails (e.g., `yoursubdomain.yourdomain.com`)
   - Using a subdomain isolates your email sending reputation from your main domain
   - Example: If your domain is `example.com`, use `yoursubdomain.example.com`

2. Add DNS Records
   - Log into your domain registrar or DNS provider
   - Add an A record for your subdomain pointing to Mailjet's servers
   - Add the subdomain to your Mailjet account in Sender Domains section

## SPF Setup

SPF (Sender Policy Framework) helps prevent email spoofing. Add this TXT record to your DNS:

```
Type: TXT
Host: yoursubdomain
Value: v=spf1 include:spf.mailjet.com ?all
```

Note: If you already have an SPF record, add `include:spf.mailjet.com` to the existing record.

## DKIM Setup

DKIM (DomainKeys Identified Mail) adds a digital signature to your emails:

1. In Mailjet dashboard, go to Sender Domains
2. Select your subdomain
3. Click on "Authentication"
4. Copy the DKIM records provided by Mailjet
5. Add the records to your DNS

Example of one of the records:
```
Type: TXT
Host: mailjet._domainkey.yoursubdomain
Value: [Mailjet will provide this value]
```

## Testing Setup

Send Test Emails
- Use Mailjet's test feature to send verification emails
- Check email headers to confirm:
    - SPF passes
    - DKIM signature is valid
    - Proper subdomain usage

## SMTP Configuration

Use these settings in your application:

```
SMTP Server: in-v3.mailjet.com
Port: 587 (TLS) or 465 (SSL). I recommend 587
Username: [API Key]
Password: [Secret Key]
```

I recommend you use these SMTP settings not only for your Discourse forum, but for your NotAlone app as well.

Here's where you configure it in your app:

![SMTP Setup](images/smtp_settings.png)
