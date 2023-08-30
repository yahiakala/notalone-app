from ._anvil_designer import ItemTemplate3Template
from anvil import *


class ItemTemplate3(ItemTemplate3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.pmt_success = 'Member is in good standing with payments.'
        if self.item['payment_email']:
            pmt_email = self.item['payment_email']
        else:
            pmt_email = ''
        self.pmt_fail = 'The member has not paid or is not using the email(s): ' + self.item['email'] + ', ' + pmt_email
        self.lbl_payment_status.text = self.pmt_success if self.item['payment_enrolled'] else self.pmt_fail

    def btn_remove_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['roles'] = []
        self.parent.raise_event('x-refresh1')

    def btn_ban_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['roles'] = ['banned']
        self.parent.raise_event('x-refresh1')


