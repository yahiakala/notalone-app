from ._anvil_designer import PlanRowTemplate
from anvil import *


class PlanRow(PlanRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_show_roles_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.plan_role_perm = ''
