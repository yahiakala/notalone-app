from ._anvil_designer import ForumiComponentTemplate
from anvil import *


class ForumiComponent(ForumiComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        print('changing url')
        # self.call_js('setIframeSrc', "https://www.wikipedia.com")
        # pass
    def show(self, **event_args):
        print('show event')