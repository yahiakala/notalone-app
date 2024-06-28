from ._anvil_designer import BudgetTemplateTemplate
from anvil import *

from ..Global import Global


class BudgetTemplate(BudgetTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def btn_del_budget_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.finances['budgets'] = [i for i in Global.finances['budgets'] if self.item != i]
        self.parent.raise_event('x-refresh')

