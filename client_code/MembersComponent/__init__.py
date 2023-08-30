from ._anvil_designer import MembersComponentTemplate
from anvil import *

from .. import Global


class MembersComponent(MembersComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        print("Client: Getting members ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.members = Global.users.search(roles=['member'])
        print("Client: Got members ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.init_components(**properties)
        print("Client: Got data bindings ", dt.datetime.now().strftime("%H:%M:%S.%f"))

        self.rp_members.add_event_handler('x-refresh1', self.update_stuff)

    def update_stuff(self, **event_args):
        self.members = Global.users.search(roles=['member'])
        self.refresh_data_bindings()
