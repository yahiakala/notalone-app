from ._anvil_designer import ProfileComponentTemplate
from anvil import *
import anvil.server

from .. import Global


class ProfileComponent(ProfileComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = dict(Global.user)
        self.lbl_10 = 'https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-4KE37959PY660271HMCR4POQ'
        self.lbl_50 = 'https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-97F27333BM300020TMCR4PGI'
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

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
