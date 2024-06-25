import anvil.server
import anvil.users
import anvil.js



class GlobalCache:
    def __init__(self):
        self._global_dict = {
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

    def __getattr__(self, name):
        if name in self._global_dict:
            if name == 'user':
                self._global_dict[name] = self._global_dict[name] or anvil.users.get_user()
            elif name == 'is_mobile':
                self._global_dict[name] = self._global_dict[name] or anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
            else:
                self._global_dict[name] = self._global_dict[name] or anvil.server.call('get_' + name)
            return self._global_dict[name]
        raise AttributeError(f"Attribute {name} not found")

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # This allows initialization and internal attributes to be set.
            super().__setattr__(name, value)
        else:
            if value is None:
                # If setting an attribute to None, remove it to force repopulation on next access.
                self._global_dict.pop(name, None)
            else:
                # For all other assignments, update the global dictionary normally.
                self._global_dict[name] = value

    def clear_global_attributes(self):
        for name in list(self._global_dict.keys()):
            self._global_dict[name] = None

# Initialize the global cache instance
Global = GlobalCache()
