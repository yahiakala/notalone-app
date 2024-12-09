# Database Schema Documentation

## Overview

The Not Alone application uses several interconnected tables to manage users, roles, permissions, tenants, and various other features. This document outlines the database schema and relationships between tables.

## Tables

### Users
Primary user account information and authentication.

**Note:** Several columns in this table are obsolete and have been superseded by columns in the `usermap` table.

#### Columns
- email (string): Primary identifier for users
- enabled (boolean): Whether the account is active
- last_login (datetime): Last user login timestamp
- password_hash (string): Hashed user password
- n_password_failures (number): Count of failed login attempts
- confirmed_email (boolean): Email verification status
- remembered_logins (simpleObject): Stored login sessions
- mfa (simpleObject): Multi-factor authentication settings
- signed_up (datetime): Account creation timestamp
- email_confirmation_key (string): Email verification token

### Usermap
Maps users to tenants and roles, containing user-tenant specific data. This table supersedes several columns from the users table.

#### Columns
- user (link_single → users): Reference to user account
- roles (link_multiple → roles): User's roles within tenant
- tenant (link_single → tenants): Associated tenant
- notes (string): User-specific notes
- fee (number): User's fee amount
- paypal_sub_id (string): PayPal subscription identifier
- consent_check (boolean): User consent status
- booking_link (string): User's booking link
- payment_expiry (date): Payment expiration date
- payment_status (string): Current payment status
- discord (string): Discord identifier
- phone (string): Contact phone number
- screening_slots (simpleObject): Available screening slots
- first_name (string): User's first name
- last_name (string): User's last name

### Tenants
Organization/tenant configuration and settings.

#### Columns
- email (string): Primary contact email
- name (string): Organization name
- waiver (string): Waiver document/link
- logo (media): Organization logo
- discourse_api_key (string): Discourse API credentials
- discourse_secret (string): Discourse API secret
- paypal_client_id (string): PayPal integration ID
- paypal_plans (simpleObject): PayPal plan configurations
- paypal_secret (string): PayPal API secret
- discourse_url (string): Discourse forum URL
- discord_invite (string): Discord invite link
- paypal_webhook_id (string): PayPal webhook identifier
- paypal_webhook_certificate (string): PayPal webhook certificate
- new_roles (simpleObject): Role configurations
- custom_reports (simpleObject): Custom report settings
- smtp_email (string): SMTP email configuration

### Roles
Role definitions and permissions.

#### Columns
- name (string): Role name
- reports_to (string): Reporting hierarchy
- tenant (link_single → tenants): Associated tenant
- guide (media): Role guide document
- last_update (date): Last modification date
- permissions (link_multiple → permissions): Associated permissions
- can_edit (boolean): Edit permission flag

### Permissions
System permissions definitions.

#### Columns
- name (string): Permission identifier
- description (string): Permission description

### Files
File storage and management.

#### Columns
- path (string): File path/location
- file (media): Stored file
- file_version (string): Version identifier

### RoleFiles
Role-specific file associations.

#### Columns
- name (string): File name
- file (media): Associated file
- role (link_single → roles): Related role

### Notes
User/tenant specific notes.

#### Columns
- notes (string): Note content
- user (link_single → users): Associated user
- tenant (link_single → tenants): Associated tenant

### Forum
Forum/chat integration settings.

#### Columns
- discourse_secret (string): Discourse API secret
- discourse_url (string): Discourse forum URL
- tenant (link_single → tenants): Associated tenant
- discord_invite (string): Discord invite link

### Finances
Financial tracking and budgeting.

#### Columns
- rev_12 (number): Revenue metric
- budgets (simpleObject): Budget configurations
- tenant (link_single → tenants): Associated tenant
- rev_12_active (number): Active revenue metric

## Key Relationships

1. Users → Tenants: Users belong to tenants through both the users table and usermap table
2. Users → Roles: Users are assigned roles through the usermap table
3. Roles → Permissions: Roles have multiple associated permissions
4. Roles → RoleFiles: Roles can have associated files
5. Tenants → Forum: Tenants have associated forum configurations
6. Tenants → Finances: Tenants have associated financial records

## Migration Notes

The application has undergone a schema evolution where user-tenant specific data was moved from the users table to the usermap table. This allows for better multi-tenant support and cleaner separation of concerns. When working with user data, prefer the fields in usermap over their counterparts in the users table.
