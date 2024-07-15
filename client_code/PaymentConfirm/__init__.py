from ._anvil_designer import PaymentConfirmTemplate
from anvil import *
import anvil.server
from ..Global import Global
from anvil_extras import routing

@routing.route('/paymentconfirm')
class PaymentConfirm(PaymentConfirmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def ti_payment_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        self.email = Global.user['email']
        self.member = anvil.server.call('get_member_data', Global.tenant_id, self.email)
        if 'Member' in self.member['roles']:
            self.ti_payment.interval = 0
            routing.clear_cache()
            Global.permissions = self.member['permissions']
            routing.set_url_hash('app/home')
