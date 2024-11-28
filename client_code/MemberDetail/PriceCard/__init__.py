import anvil.server
from anvil import *
from anvil_squared.utils import print_timestamp

from ._anvil_designer import PriceCardTemplate


class PriceCard(PriceCardTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.lbl_name.text = self.item["name"]
        self.lbl_amt.text = "Price: " + str(self.item["amt"])
        self.lbl_frequency.text = self.item["frequency"]

    def btn_pay_link_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_pay_link.text = "Redirecting..."
        self.btn_pay_link.italic = True
        self.parent.raise_event("x-pay-click", item=self.item)
