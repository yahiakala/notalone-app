from ._anvil_designer import VolunteerComponentTemplate
from anvil import *

class VolunteerComponent(VolunteerComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_add_click(self, **event_args):
        """Add a volunteer role, refresh repeating panel."""
        pass
