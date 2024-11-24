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
        print('paymentconfirm')

    def ti_payment_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        self.email = Global.user['email']
        with anvil.server.no_loading_indicator:
            self.member = anvil.server.call('get_member_data', Global.tenant_id, self.email)
            print('ti_payment_tick')
            if 'Member' in self.member['roles']:
                self.ti_payment.interval = 0
                Global.permissions = self.member['permissions']
                print('Payment confirmed!')
                self.label_1.visible = False
                self.image_1.visible = False
                self.lbl_confirmed.visible = True
                routing.clear_cache()
            
