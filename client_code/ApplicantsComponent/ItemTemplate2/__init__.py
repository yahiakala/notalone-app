from ._anvil_designer import ItemTemplate2Template
from anvil import *
import anvil.server

from ... import Global


class ItemTemplate2(ItemTemplate2Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.pmt_success = 'The applicant has paid.'
        if self.item['payment_email']:
            pmt_email = self.item['payment_email']
        else:
            pmt_email = ''
        self.pmt_fail = 'The applicant has not paid or is not using the email(s): ' + self.item['email'] + ', ' + pmt_email
        self.lbl_payment_status.text = self.pmt_success if self.item['payment_enrolled'] else self.pmt_fail
        self.btn_added.visible = self.item['payment_enrolled']

    def btn_added_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.applicants = anvil.server.call('reassign_roles', self.item, ['member'])
        self.parent.raise_event('x-refresh1')