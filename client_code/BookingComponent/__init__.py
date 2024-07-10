from ._anvil_designer import BookingComponentTemplate
from anvil import *
from anvil_extras import routing
from ..Global import Global


@routing.route('/apply', template='Router')
class BookingComponent(BookingComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.item = Global.screenerlink
        self.init_components(**properties)
