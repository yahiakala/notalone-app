from ._anvil_designer import MembersComponentTemplate
from anvil import *

from .. import Global


class MembersComponent(MembersComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.members = Global.users.search(roles=['member'])
        self.init_components(**properties)

        self.rp_members.add_event_handler('x-refresh1', self.update_stuff)

    def update_stuff(self, **event_args):
        self.members = Global.users
        self.refresh_data_bindings()
