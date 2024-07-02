from ._anvil_designer import MemberRowTemplate
from anvil import *


class MemberRow(MemberRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def link_email_click(self, **event_args):
        """This method is called when the link is clicked"""
        pass
