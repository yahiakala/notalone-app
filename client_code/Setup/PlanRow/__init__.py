from ._anvil_designer import PlanRowTemplate
from anvil import *
from ...Global import Global
from anvil_extras import routing


class PlanRow(PlanRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.lbl_roles = ', '.join(self.item['roles'])

    def btn_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass
