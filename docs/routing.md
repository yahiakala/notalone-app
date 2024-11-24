# Hash-Based Routing Documentation

## Overview

The Not Alone app uses `anvil_extras.routing` for client-side navigation through hash-based routing. This enables single-page application (SPA) behavior with clean URLs and browser history support.

## Routing Architecture

### Template System

The app uses two main templates for routing:

1. `Router` template - Main application layout with sidebar navigation
2. `Static` template - Used for authentication pages (sign in/up)

The Router template is decorated with a condition to ensure the tenant is set:

```python
@routing.template(path='app', priority=5, condition=lambda: Global.get_s('tenant') is not None)
class Router(RouterTemplate):
    # ...
```

### URL Structure

URLs in the application follow these patterns:

- Authentication: `#sign`, `#signin`, `#signup`
- Main app: `#app/[section]`
- Detail views: `#app/[section]/[id]`

## Route Definitions

### Authentication Routes

```python
@routing.route('', template='Static')
@routing.route('sign', template='Static', url_keys=[routing.ANY])
class Sign(SignTemplate):
    # ...

@routing.route('signin', template='Static', url_keys=[routing.ANY])
class Signin(SigninTemplate):
    # ...

@routing.route('signup', template='Static', url_keys=[routing.ANY])
class Signup(SignupTemplate):
    # ...
```

### Main Application Routes

```python
@routing.route('/home', template='Router')
class Home(HomeTemplate):
    # ...

@routing.route('/members', template='Router', url_keys=[routing.ANY])
class Members(MembersTemplate):
    # ...

@routing.route('/volunteers', template='Router')
class Roles(RolesTemplate):
    # ...
```

### Detail View Routes

```python
@routing.route("/memberdetail", template="Router", url_keys=['user_email'])
@routing.route('/profile', template='Router')
class MemberDetail(MemberDetailTemplate):
    # ...

@routing.route('/roledetail', template='Router', url_keys=['role'])
class RoleDetail(RoleDetailTemplate):
    # ...
```

## Navigation Implementation

### URL Hash Management

The Router component manages URL hashes for navigation links:

```python
def __init__(self, **properties):
    self.init_components(**properties)
    
    self.link_home.tag.url_hash = 'app/home'
    self.link_apply.tag.url_hash = 'app/apply'
    self.link_profile.tag.url_hash = 'app/profile'
    self.link_members.tag.url_hash = 'app/members'
    self.link_fin.tag.url_hash = 'app/financials'
    self.link_volunteers.tag.url_hash = 'app/volunteers'
    self.link_admin.tag.url_hash = 'app/admin'
    self.link_reports.tag.url_hash = 'app/reports'
    self.link_settings.tag.url_hash = 'app/settings'
```

### Navigation Events

The Router handles navigation events and updates UI state:

```python
def nav_click(self, sender, **event_args):
    if sender.tag.url_hash == '':
        if Global.user:
            self.set_account_state(Global.user)
            routing.set_url_hash('app')
        else:
            routing.set_url_hash('')
    else:
        routing.set_url_hash(sender.tag.url_hash)

def on_navigation(self, url_hash, url_pattern, url_dict, unload_form):
    # Update selected state of navigation links
    for link in self.cp_sidebar.get_components():
        if type(link) == Link:
            link.role = 'selected' if link.tag.url_hash == url_hash else None
    if url_hash in ['homeanon', 'homedetail', 'app']:
        self.link_home.role = 'selected'
```

## Route Parameters

Some routes accept parameters through `url_keys`:

1. Member Detail View:
```python
@routing.route("/memberdetail", template="Router", url_keys=['user_email'])
```
- Accepts user email as parameter
- URL format: `#app/memberdetail?user_email=example@email.com`

2. Role Detail View:
```python
@routing.route('/roledetail', template='Router', url_keys=['role'])
```
- Accepts role identifier as parameter
- URL format: `#app/roledetail?role=role_id`

## Authentication and Routing

The routing system integrates with authentication:

```python
def link_logout_click(self, **event_args):
    with anvil.server.no_loading_indicator:
        anvil.users.logout()
        self.set_account_state(None)
        routing.clear_cache()
        Global.clear_global_attributes()
        routing.set_url_hash('sign', load_from_cache=False)
```

Key features:
- Clears routing cache on logout
- Redirects to sign-in page
- Prevents cached data from persisting across sessions

## Best Practices

1. **Template Selection**
   - Use `Router` template for authenticated pages
   - Use `Static` template for authentication flows

2. **URL Parameters**
   - Use `url_keys` for required parameters
   - Use `routing.ANY` for optional parameters

3. **Navigation State**
   - Update selected states in `on_navigation`
   - Clear cache when logging out
   - Use `routing.set_url_hash()` for programmatic navigation

4. **Conditional Routes**
   - Use template conditions for access control
   - Check permissions before allowing navigation

5. **Cache Management**
   - Clear routing cache when user state changes
   - Use `load_from_cache=False` when fresh data is required
