from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server

from ... import Global


class ItemTemplate2(ItemTemplate2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.pmt_success = 'The applicant has paid.'
        self.pmt_fail = 'The applicant has not paid'
        self.lbl_payment_status.text = self.pmt_success if self.item['good_standing'] else self.pmt_fail
        self.btn_added.visible = self.item['good_standing']

    def btn_added_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item = anvil.server.call('reassign_roles', self.item, ['member'])
        self.parent.raise_event('x-refresh1')