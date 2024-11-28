import anvil.server
from anvil import *
from anvil_extras import routing

from ..Global import Global
from ._anvil_designer import PaymentConfirmTemplate


@routing.route("/paymentconfirm")
class PaymentConfirm(PaymentConfirmTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        print("paymentconfirm")

    def ti_payment_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        self.email = Global.user["email"]
        with anvil.server.no_loading_indicator:
            self.member = anvil.server.call(
                "get_member_data", Global.tenant_id, self.email
            )
            print("ti_payment_tick")
            if self.member["payment_status"] == "ACTIVE":
                self.ti_payment.interval = 0
                Global.permissions = self.member["permissions"]
                print("Payment confirmed!")
                self.label_1.visible = False
                self.image_1.visible = False
                self.lbl_confirmed.visible = True
                routing.clear_cache()
