from ._anvil_designer import PlanRowTemplate
from anvil import *
from ...Global import Global
from ..RoleSelect import RoleSelect
from anvil_extras import routing


class PlanRow(PlanRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_show_roles_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.plan_role_perm = {}
        self.plan_role_perm['roles'] = self.item['roles'].copy()
        self.plan_role_perm['roles'] = [i for i in Global.roles if i['name'] in self.item['roles']]
        new_roles = routing.alert(RoleSelect(item=self.plan_role_perm))
        if new_roles:
            print(new_roles)

    def btn_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
