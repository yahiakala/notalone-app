from ._anvil_designer import FinComponentTemplate
from anvil import *

# TODO: bar chart of number of subs per plan_id
# TODO: bar chart of amounts coming from each plan_id

# TODO: count of members with zero fee (and drill down)

# TODO: count of members with expired or no subscription
# TODO: calc amount lost from expired or non-subs

# TODO: Bar chart of last payments throughout the year

from .. import Global


class FinComponent(FinComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.finances = Global.finances
        self.init_components(**properties)
        self.rp_budget.add_event_handler('x-refresh', self.refresh_data)

    def btn_save_budget_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.finances['budgets'] = self.finances['budgets'] + [
            {'name': self.tb_budg_name.text, 'amount': self.tb_budget_amt.text}
        ]
        Global.finances = self.finances
        self.cp_add_budget.visible = False
        self.btn_add_budget.visible = True
        self.refresh_data_bindings()

    def btn_add_budget_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_add_budget.visible = False
        self.cp_add_budget.visible = True

    def refresh_data(self, **event_args):
        self.refresh_data_bindings()


        
