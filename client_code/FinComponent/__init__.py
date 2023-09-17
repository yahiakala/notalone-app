from ._anvil_designer import FinComponentTemplate
from anvil import *

# TODO: bar chart of number of subs per plan_id
# TODO: bar chart of amounts coming from each plan_id

# TODO: count of members with zero fee (and drill down)

# TODO: count of members with expired or no subscription
# TODO: calc amount lost from expired or non-subs

# TODO: Bar chart of last payments throughout the year
# TODO: projected 12 month revenue from active subs

class FinComponent(FinComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        
