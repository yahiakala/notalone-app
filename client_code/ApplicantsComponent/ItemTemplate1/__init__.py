from ._anvil_designer import ItemTemplate1Template
from anvil import *
import anvil.server

from .. import Global


class ItemTemplate1(ItemTemplate1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)


    def btn_accept_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.applicants = anvil.server.call('reassign_roles', self.item, ['pending'])
        self.parent.raise_event('x-refresh1')

    def btn_reject_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.applicants = anvil.server.call('reassign_roles', self.item, ['rejected'])
        self.parent.raise_event('x-refresh1')
