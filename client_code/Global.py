from anvil_squared.utils import GlobalCache


_global_dict = {
    'user': None,
    'is_mobile': None,
    'usermap': None,
    'user_data': None,
    'tenant_id': None,
    'permissions': None,
    'users': None,
    'tenants': None,
    'applied': None,
    'applicants': None,
    'pending': None,
    'screener_link': None,
    'finances': None,
    'forumlink': None,
    'roles_to_members': None,
    'roles': None,
    'super_load': None,
    'discordlink': None
}

Global = GlobalCache(_global_dict)