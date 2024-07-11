from ._anvil_designer import PlanEditTemplate
from anvil import *
from ...Global import Global


class PlanEdit(PlanEditTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.msdd_roles.items = [
            {
                'key': i['name'],
                'value': i['name'],
                'subtext': ', '.join(i['permissions'])
            }
            for i in Global.roles
        ]
        
        if self.item:
            self.tb_plan_id.text = self.item['id']
            self.tb_plan_name.text = self.item['name']
            self.tb_plan_amt.text = self.item['amt']
            self.tb_plan_frequency.text = self.item['frequency']
            self.msdd_roles.selected = self.item['roles']

    def btn_cancel_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.raise_event('x-close-alert', value=None)

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        plan_dict = {
            'id': self.tb_plan_id.text,
            'name': self.tb_plan_name.text, 
            'amt': self.tb_plan_amt.text,
            'frequency': self.tb_plan_frequency.text,
            'roles': self.msdd_roles.selected
        }
        self.raise_event('x-close-alert', value=plan_dict)
