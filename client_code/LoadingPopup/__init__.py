from ._anvil_designer import LoadingPopupTemplate
from anvil import *
from ..Global import Global
import time


class LoadingPopup(LoadingPopupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def check_if_loaded(self):
        for key in self.item:
            if Global.get_no_call(key) is None:
                return False
        return True

    def ti_load_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.check_if_loaded():
            self.raise_event('x-close-alert', value=True)
