from ._anvil_designer import RolesTemplate
from anvil import *
import anvil.server
from ..Global import Global
from anvil_extras import routing


@routing.route('/volunteers', template='Router')
class Roles(RolesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = Global.user
        self.init_components(**properties)

        if 'see_members' in Global.permissions:
            self.rp_vol_roles.items = Global.roles_to_members
        else:
            self.rp_vol_roles.items = Global.roles
        # Any code you write here will run before the form opens.

    def btn_add_click(self, **event_args):
        """Add a volunteer role, refresh repeating panel."""
        self.cp_addrole.visible = True

    def btn_save_new_role_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.roles_to_members = anvil.server.call('add_role',
                                                    self.tb_new_role.text,
                                                    self.tb_new_role_report.text, Global.roles_to_members)
        self.rp_vol_roles.items = Global.roles_to_members
        self.lbl_new_role.text = None
        self.lbl_new_role_reports.text = None
        self.cp_addrole.visible = False
