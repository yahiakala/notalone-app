from ._anvil_designer import ApplicantsComponentTemplate
from anvil import *
import anvil.server
import anvil.tables.query as q

from .. import Global

import datetime as dt


class ApplicantsComponent(ApplicantsComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.rp_applicants.add_event_handler('x-refresh', self.populate_rp)
        self.rp_pending.add_event_handler('x-refresh', self.populate_rp)
        self.populate_rp()

    def populate_rp(self, **event_args):
        self.rp_applicants.items = Global.applicants.search(
            auth_profile=q.not_(True),
            auth_booking=True
        )
        self.rp_pending.items = Global.applicants.search(
            auth_profile=True
        )
        self.raise_event('x-refresh')
