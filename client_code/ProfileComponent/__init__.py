from ._anvil_designer import ProfileComponentTemplate
from anvil import *
import anvil.server

from .. import Global


class ProfileComponent(ProfileComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = dict(Global.user)  # Avoid errors with data bindings
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.user['first_name'] == '' or self.user['last_name'] == '':
            self.lbl_namealert.visible = True
        else:
            self.lbl_namealert.visible = False
        Global.user = anvil.server.call('update_user', self.user)
        self.user = dict(Global.user)

    def tb_donation_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.link_payment.url = (
            '' if not self.tb_donation.text
            else self.lbl_10 if self.tb_donation.text < 50
            else self.lbl_50
        )

    def btn_pay_new_click(self, **event_args):
        """This method is called when the button is clicked"""
        from anvil.js import window
        fee_send = self.user['fee']
        if not self.user['fee']:
            fee_send = 10

        self.user, self.payment_url = anvil.server.call(
            'create_sub', fee_send
        )
        self.user = dict(self.user)  # avoid errors with data bindings
        self.btn_save_click()
        window.open(self.payment_url)
        window.location = self.payment_url
        self.refresh_data_bindings()
        self.raise_event('x-go-home')



