from ._anvil_designer import BookingComponentTemplate
from anvil import *

from .. import Global

class BookingComponent(BookingComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.item = Global.screener_link
        self.init_components(**properties)
