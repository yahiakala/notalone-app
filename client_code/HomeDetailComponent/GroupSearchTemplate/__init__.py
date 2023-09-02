from ._anvil_designer import GroupSearchTemplateTemplate
from anvil import *
import anvil.server

from ... import Global


class GroupSearchTemplate(GroupSearchTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_join_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.user = anvil.server.call('join_tenant', self.item.get_id())
        self.parent.raise_event('x-refresh')

