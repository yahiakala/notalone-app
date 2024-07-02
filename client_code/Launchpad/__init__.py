from ._anvil_designer import LaunchpadTemplate
from anvil import *
import anvil.server
from anvil_extras import routing
from ..Global import Global
import anvil.tables.query as q
from anvil_squared.utils import print_timestamp


@routing.route('', template='StaticLaunch')
class Launchpad(LaunchpadTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.rp_my_groups.items = [None]
        self.rp_groups.items = [None]
        print_timestamp('loaded launcher')

    def btn_create_group_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('create_tenant', self.user)

    def tb_search_group_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        search_txt = '%' + self.tb_search_group.text + '%'
        self.groups = Global.tenants.search(
            name=q.ilike(search_txt)
        )
        self.btn_clear_search.visible = True
        self.rp_groups.items = self.groups

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.groups = []
        self.tb_search_group.text = None
        self.btn_clear_search.visible = False
        self.rp_groups.items = self.groups

    def ti_load_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        self.ti_load.interval = 0
        with anvil.server.no_loading_indicator:
            self.user = Global.user
            self.my_tenants = Global.my_tenants
    
            if Global.get_s('permissions') and 'create_tenant' in Global.get_s('permissions'):
                self.btn_create_group.visible = True
    
            self.rp_my_groups.items = self.my_tenants
            self.tb_search_group_pressed_enter()
