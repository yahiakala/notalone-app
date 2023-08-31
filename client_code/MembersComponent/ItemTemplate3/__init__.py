from ._anvil_designer import ItemTemplate3Template
from anvil import *
import anvil.server

import datetime as dt


class ItemTemplate3(ItemTemplate3Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        print("Client: Getting member data binding ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.init_components(**properties)
        print("Client: Got member data binding ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.pmt_success = 'Member is in good standing with payments.'
        self.pmt_noid = 'Member has no linked paypal subscription.'
        self.pmt_inactive = "Member's paypal subscription is inactive."
        self.lbl_payment_status.text = (
            self.pmt_success if self.item['payment_enrolled'] else
            self.pmt_inactive if self.item['paypal_sub_id'] is not None else
            self.pmt_noid
        )

    
    def btn_remove_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['roles'] = ['removed']
        self.parent.raise_event('x-refresh1')

    def btn_ban_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['roles'] = ['banned']
        self.parent.raise_event('x-refresh1')

    def btn_left_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['roles'] = ['left']
        self.parent.raise_event('x-refresh1')

    def btn_screener_click(self, **event_args):
        """This method is called when the button is clicked"""
        if 'screener' not in self.item['roles']:
            self.item['roles'] = self.item['roles'] + ['screener']
        self.btn_screener.visible = False

    def btn_leader_click(self, **event_args):
        """This method is called when the button is clicked"""
        if 'leader' not in self.item['roles']:
            self.item['roles'] = self.item['roles'] + ['leader']
        self.btn_leader.visible = False

    def btn_refresh_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item = anvil.server.call('check_sub')
        self.refresh_data_bindings()






