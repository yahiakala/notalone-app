from ._anvil_designer import ProfileComponentTemplate
from anvil import *
import anvil.server

from .. import Global


class ProfileComponent(ProfileComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = dict(Global.user)  # so I can save over it
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.slots = [
            {
                "day": 0,
                "end": 17,
                "start": 9,
                "available": True
            },
            {
                "day": 1,
                "end": 17,
                "start": 9,
                "available": True
            },
            {
                "day": 2,
                "end": 17,
                "start": 9,
                "available": True
            },
            {
                "day": 3,
                "end": 17,
                "start": 9,
                "available": True
            },
            {
                "day": 4,
                "end": 17,
                "start": 9,
                "available": True
            },
            {
                "day": 5,
                "end": 17,
                "start": 9,
                "available": True
            },
            {
                "day": 6,
                "end": 17,
                "start": 9,
                "available": True
            }
        ]
        from .DaySelector import DaySelector
        for slot in self.slots:
            self.fp_daily.add_component(DaySelector(item=slot))
        # TODO: integrate with existing save button

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.user = anvil.server.call('update_user', self.user)
        Global.user = self.user

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
        self.btn_save_click()
        window.open(self.payment_url)
        window.location = self.payment_url
        self.refresh_data_bindings()
        self.raise_event('x-go-home')



