from ._anvil_designer import ItemTemplate1Template
from anvil import *

class ItemTemplate1(ItemTemplate1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_accept_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_reject_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass


