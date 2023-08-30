from ._anvil_designer import HomeDetailComponentTemplate
from anvil import *

class HomeDetailComponent(HomeDetailComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
