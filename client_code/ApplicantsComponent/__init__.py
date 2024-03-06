from ._anvil_designer import ApplicantsComponentTemplate
from anvil import *
import anvil.server
import anvil.tables.query as q
from anvil_extras import routing
from .. import Global

import datetime as dt


@routing.route('/applicants', template='Router')
class ApplicantsComponent(ApplicantsComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.rp_applicants.add_event_handler('x-refresh', self.refresh_rp)
        # self.rp_pending.add_event_handler('x-refresh', self.populate_rp)
        self.populate_rp()

    def populate_rp(self, **event_args):
        self.rp_applicants.items = Global.applicants
        self.refresh_data_bindings()

    def refresh_rp(self, **event_args):
        Global.applicants = anvil.server.call('get_applicants')
        self.rp_applicants.items = Global.applicants
        self.refresh_data_bindings()
