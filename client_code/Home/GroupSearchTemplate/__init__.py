from ._anvil_designer import GroupSearchTemplateTemplate
from anvil import *
import anvil.server
from anvil_extras import routing

from ...Global import Global


class GroupSearchTemplate(GroupSearchTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.my_tenants = Global.my_tenants
        # Any code you write here will run before the form opens.

    def btn_join_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.user = anvil.server.call('join_tenant', self.item.get_id())
        Global.tenant_id = self.item.get_id()
        self.my_tenants = self.my_tenants + [{'tenant_id': self.item.get_id(), 'name': self.item['name']}]
        routing.set_url_hash('app')

