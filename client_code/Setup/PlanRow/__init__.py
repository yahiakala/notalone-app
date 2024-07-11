from ._anvil_designer import PlanRowTemplate
from anvil import *
from anvil_extras import routing
import anvil.server
from ..PlanEdit import PlanEdit


class PlanRow(PlanRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.lbl_roles.text = ', '.join(self.item['roles'])

    def btn_delete_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.parent.raise_event('x-remove-plan', item=self.item)

    def btn_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            new_plan = routing.alert(PlanEdit(item=self.item), dismissible=False, buttons=None)
            if new_plan:
                self.parent.raise_event('x-edit-plan', item=new_plan)
