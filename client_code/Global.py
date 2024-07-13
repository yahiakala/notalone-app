from anvil_squared.globals import GlobalCache


_global_dict = {
    'user': None,
    'is_mobile': None,
    'tenant': None,
    'tenant_id': None,
    'tenants': None,
    'my_tenants': None
}
_tenanted_dict = {
    'usermap': None,
    'permissions': None,
    'users': None,
    'screenerlink': None,
    'finances': None,
    'roles': None
}

Global = GlobalCache(_global_dict, _tenanted_dict)