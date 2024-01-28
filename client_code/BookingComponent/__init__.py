from ._anvil_designer import BookingComponentTemplate
from anvil import *
from anvil_extras import routing
from .. import Global


@routing.route('apply')
class BookingComponent(BookingComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.item = Global.screener_link
        self.init_components(**properties)
