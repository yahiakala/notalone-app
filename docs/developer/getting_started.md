# Getting Started Guide

This guide will help you set up your development environment for contributing to the Not Alone app. The app is built using [Anvil's web framework](https://anvil.works) and integrates with several external services.

## Prerequisites

Before starting, ensure you have:

- A GitHub account
- A PayPal business account
- A DigitalOcean account (for Discourse hosting)
- Basic knowledge of Python and web development

## 1. Anvil Setup

1. Visit [anvil.works](https://anvil.works)
2. Sign up for a free account
3. Choose the "Free" plan (sufficient for development)

## 2. Fork and Clone Repositories

### Main Application Repository

1. Fork the Not Alone repository:
    - Visit https://github.com/yahiakala/notalone-app
    - Click "Fork" button
    - Go to your Anvil.works account and click "Clone from GitHub" under the "Create a new app" section.
    - Enter the URL to your forked repo, and authenticate with your GitHub account.
    - Click "Clone App"

2. Set up dependencies
    - Go to Settings > Dependencies
    - Use the pencil icon to edit your dependencies, but do not change the versions.
    - Make sure the anvil_extras dependency is set to point to a third party dependency with dependency ID C6ZZPAPN4YYF5NVJ. [See here for more info](https://github.com/anvilistas/anvil-extras). Use the pencil icon. Do not change the tag.
    - Make sure the anvil_squared dependency is set to point to a third party dependency with dependency ID KDKDM3MG6IQHC2FK. Use the pencil icon. Do not change the tag.

### Local Development Setup

Not even going to go into this, you'd have to be an expert to figure this out.

## 3. Set up Mailjet and Discourse
See [Discourse Setup](../admin/discourse_setup.md)

## 4. Set up PayPal
See [PayPal Setup](../admin/paypal_setup.md)

## 10. Additional Resources

- [Anvil Documentation](https://anvil.works/docs)
- [PayPal Developer Docs](https://developer.paypal.com/docs)
- [Discourse API Guide](https://docs.discourse.org)
- Project-specific docs in `/docs` directory
