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
