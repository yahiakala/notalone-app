from ._anvil_designer import ApplicantsComponentTemplate
from anvil import *
import anvil.server

from .. import Global

import datetime as dt


class ApplicantsComponent(ApplicantsComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        # print("Client: Getting Applicants ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        print("Client: Getting applied ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.applied = Global.applied

        print("Client: Getting pending ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.pending = Global.pending
        print("Client: Getting data bindings ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.init_components(**properties)
        print("Client: Done getting data bindings ", dt.datetime.now().strftime("%H:%M:%S.%f"))

        # print('Pending Applicants: ', [i for i in self.applicants if 'pending' in i['roles']])
        self.rp_applicants.add_event_handler('x-refresh1', self.update_stuff)
        self.rp_pending.add_event_handler('x-refresh1', self.update_stuff)


    def update_stuff(self, **event_args):
        # self.applicants = Global.applicants
        Global.applied = anvil.server.call('get_applied')
        self.applied = Global.applied
        Global.pending = anvil.server.call('get_pending')
        self.pending = Global.pending
        self.refresh_data_bindings()