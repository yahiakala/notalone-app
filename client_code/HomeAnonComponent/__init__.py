from ._anvil_designer import HomeAnonComponentTemplate
from anvil import *
import anvil.server


class HomeAnonComponent(HomeAnonComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
