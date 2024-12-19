from anvil import *

from ._anvil_designer import ChipTemplate


class Chip(ChipTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def btn_chip_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.parent.raise_event("x-remove", remove=self.item["name"])
