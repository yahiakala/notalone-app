from anvil import *

from ._anvil_designer import MFAItemTemplate


class MFAItem(MFAItemTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_delete_click(self, **event_args):
        """Start process of deleting MFA method."""
        self.cp_pw.visible = True

    def btn_confirm_click(self, **event_args):
        """Confirm delete MFA method."""
        self.cp_pw.visible = False
        self.parent.raise_event(
            "x-remove-mfa-id", id=self.item["id"], password=self.tb_enter_pw.text
        )
