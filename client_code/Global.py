from anvil_squared.utils import GlobalCache


_global_dict = {
    'user': None,
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