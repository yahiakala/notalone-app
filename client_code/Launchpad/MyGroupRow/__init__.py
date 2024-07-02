from ._anvil_designer import MyGroupRowTemplate
from anvil import *
from ...Global import Global
from anvil_extras import routing


class MyGroupRow(MyGroupRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        if self.item:
            self.lbl_name.text = self.item['name']
        else:
            self.lbl_name.text = ' ' * 500
            self.lbl_name.role = 'skeleton'

    def btn_enter_group_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.tenant_id = self.item['tenant_id']
        routing.set_url_hash('app')
        
        
