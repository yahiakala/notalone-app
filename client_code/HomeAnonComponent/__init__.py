from ._anvil_designer import HomeAnonComponentTemplate
from anvil import *
from anvil_extras import routing


@routing.route('homeanon')
class HomeAnonComponent(HomeAnonComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
