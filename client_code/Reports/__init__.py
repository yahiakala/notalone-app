from anvil import *
from anvil_extras import routing

from ..Global import Global
from ._anvil_designer import ReportsTemplate


@routing.route("/reports", template="Router")
class Reports(ReportsTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.rp_reports.items = Global.tenant["custom_reports"]
