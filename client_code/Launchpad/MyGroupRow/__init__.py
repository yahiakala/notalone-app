from ._anvil_designer import MyGroupRowTemplate
from anvil import *
from ...Global import Global
from anvil_extras import routing


class MyGroupRow(MyGroupRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def link_name_click(self, **event_args):
        """This method is called when the link is clicked"""
        Global.tenant_id = self.item['tenant_id']
        routing.set_url_hash('app')
        
        
