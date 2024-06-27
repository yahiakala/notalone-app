from ._anvil_designer import GroupRowTemplate
from anvil import *
from ...Global import Global
from anvil_extras import routing
import anvil.server


class GroupRow(GroupRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.my_tenants = Global.my_tenants
        if self.my_tenants and self.item.get_id() in [i['tenant_id'] for i in self.my_tenants]:
            self.btn_join_group.visible = False

    def btn_join_group_click(self, **event_args):
        """This method is called when the button is clicked"""
        Global.user = anvil.server.call('join_tenant', self.item.get_id())
        Global.tenant_id = self.item.get_id()
        self.my_tenants = self.my_tenants + [{'tenant_id': self.item.get_id(), 'name': self.item['name']}]
        routing.set_url_hash('app')