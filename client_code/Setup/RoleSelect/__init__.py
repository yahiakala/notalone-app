from ._anvil_designer import RoleSelectTemplate
from anvil import *


class RoleSelect(RoleSelectTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.rp_roles.items = ''
        
