from ._anvil_designer import ChipzTemplate
from anvil import *
from .... import Global


class Chipz(ChipzTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = Global.user
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.parent.raise_event('x-remove', member_remove=self.item)
