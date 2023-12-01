from ._anvil_designer import ForumiComponentTemplate
from anvil import *

class ForumiComponent(ForumiComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
