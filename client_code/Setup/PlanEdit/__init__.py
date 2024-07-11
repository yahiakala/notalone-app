from ._anvil_designer import PlanEditTemplate
from anvil import *


class PlanEdit(PlanEditTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.rp_roles.items = ''
        
