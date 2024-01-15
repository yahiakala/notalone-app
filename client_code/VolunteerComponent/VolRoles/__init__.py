from ._anvil_designer import VolRolesTemplate
from anvil import *

class VolRoles(VolRolesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        assigned_members = Global.roles_to_members[self.item['name']]
        from .Chipz import Chipz
        for x in x:
            self.fp_assigned_to.add_component(Chipz(item=x))
