from ._anvil_designer import ForumComponentTemplate
from anvil import *
import anvil.server

from anvil.js.window import jQuery
from anvil.js import get_dom_node



class ForumComponent(ForumComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        # iframe = jQuery("<iframe width='100%' height='100%'>").attr("src", anvil.server.call('get_forumlink'))
        # iframe.appendTo(get_dom_node(self.outlined_card_1))
        self.link_1.url = anvil.server.call('get_forumlink')

