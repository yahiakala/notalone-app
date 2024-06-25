from ._anvil_designer import LaunchpadTemplate
from anvil import *
import anvil.server
from anvil_extras import routing
from ..Global import Global


@routing.route('launchpad', template='Static')
class Launchpad(LaunchpadTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.user = Global.user

        if 'create_group' in Global.permissions:
            self.btn_create_group.visible = True

    def btn_create_group_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('create_tenant', self.user)
