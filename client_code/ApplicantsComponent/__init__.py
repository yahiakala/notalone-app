from ._anvil_designer import ApplicantsComponentTemplate
from anvil import *
import anvil.server

from .. import Global

import datetime as dt


class ApplicantsComponent(ApplicantsComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        print("Client: Getting Applicants ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.applied = Global.applied
        print("Client: Getting applied ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.applied = [i for i in self.applicants if i['roles'] == []]
        print("Client: Getting pending ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.pending = [i for i in self.applicants if i['roles'] == ['pending']]
        print("Client: Getting data bindings ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.init_components(**properties)
        print("Client: Done getting data bindings ", dt.datetime.now().strftime("%H:%M:%S.%f"))

        print('Pending Applicants: ', [i for i in self.applicants if 'pending' in i['roles']])
        self.rp_applicants.add_event_handler('x-refresh1', self.update_stuff)
        self.rp_pending.add_event_handler('x-refresh1', self.update_stuff)


    def update_stuff(self, **event_args):
        self.applicants = Global.applicants
        self.applied = [i for i in self.applicants if i['roles'] == []]
        self.pending = [i for i in self.applicants if i['roles'] == ['pending']]
        print('Updated applicants: ', self.applicants)
        self.refresh_data_bindings()