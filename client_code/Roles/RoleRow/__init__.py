from ._anvil_designer import RoleRowTemplate
from anvil import *


class RoleRow(RoleRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_members_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        if self.item:
            self.lbl_name.text = self.item['name']
            self.lbl_last_update.text = self.item['last_update']
            self.lbl_name.role = None
            self.lbl_last_update.role = None
