from ._anvil_designer import ForumiComponentTemplate
from anvil import *
import anvil.server


class ForumiComponent(ForumiComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the HTML panel is shown on the screen"""
        self.call_js('setIframeSrc', anvil.server.call('get_forumlink'))
        # self.call_js('setIframeSrc', 'https://en.wikipedia.org/wiki/Florence_Petty')