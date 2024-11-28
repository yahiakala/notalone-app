import anvil.server
from anvil import *
from anvil_extras import routing

from ..Global import Global
from ._anvil_designer import RolesTemplate


@routing.route("/volunteers", template="Router")
class Roles(RolesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = Global.user
        self.init_components(**properties)
        self.rp_roles.items = [None, None, None]

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.rp_roles.items = Global.roles
            if "edit_roles" in Global.permissions:
                self.btn_add.visible = True
            else:
                self.btn_add.visible = False

    def btn_add_click(self, **event_args):
        """Add a volunteer role, refresh repeating panel."""
        self.cp_addrole.visible = True
        self.msdd_permissions.items = [
            {"key": i, "value": i} for i in Global.all_permissions
        ]

    def btn_save_new_role_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.roles = anvil.server.call(
            "add_role",
            Global.tenant_id,
            self.tb_new_role.text,
            self.msdd_permissions.selected,
        )
        self.rp_roles.items = Global.roles
        self.lbl_new_role.text = None
        self.cp_addrole.visible = False
