from ._anvil_designer import ApplicantsComponentTemplate
from anvil import *
import anvil.server

from .. import Global


class ApplicantsComponent(ApplicantsComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.applicants = Global.applicants
        self.init_components(**properties)

        print('Pending Applicants: ', [i for i in self.applicants if 'pending' in i['roles']])
        self.rp_applicants.add_event_handler('x-refresh1', self.update_stuff)
        self.rp_pending.add_event_handler('x-refresh1', self.update_stuff)


    def update_stuff(self, **event_args):
        self.applicants = Global.applicants
        print('Updated applicants: ', self.applicants)
        self.refresh_data_bindings()