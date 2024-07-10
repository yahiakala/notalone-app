from anvil_squared.globals import GlobalCache


_global_dict = {
    'user': None,
    'is_mobile': None,
    'usermap': None,
    'tenant': None,
    'tenant_id': None,
    'tenants': None,
    'my_tenants': None
}
_tenanted_dict = {
    # 'user_data': None,
    'usermap': None,
    'permissions': None,
    'users': None,
    # 'applied': None,
    # 'applicants': None,
    # 'pending': None,
    'screenerlink': None,
    'finances': None,
    # 'forumlink': None,
    # 'roles_to_members': None,
    'roles': None,
    # 'discordlink': None
}

Global = GlobalCache(_global_dict, _tenanted_dict)