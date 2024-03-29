from ._anvil_designer import HomeDetailComponentTemplate
from anvil import *
import anvil.tables.query as q
import anvil.server
from anvil_extras.logging import TimerLogger
from anvil_extras import routing
from .. import Global


@routing.route('', template='Router')
@routing.route('/homedetail', template='Router')
class HomeDetailComponent(HomeDetailComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.groups = []
        self.user = Global.user
        self.super_load()
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.rp_groups.add_event_handler('x-refresh', self.update_stuff)
        if self.user['tenant']:
            self.img_tenant.source = self.user['tenant']['logo']
        if not self.user['tenant']:
            self.tb_search_group_pressed_enter()

    def update_stuff(self, **event_args):
        """Refresh the whole page so the user sees the booking page."""
        self.groups = []
        self.user = Global.user
        self.refresh_data_bindings()
        routing.set_url_hash('app/apply', load_from_cache=False)

    def tb_search_group_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        search_txt = '%' + self.tb_search_group.text + '%'
        self.groups = Global.tenants.search(
            name=q.ilike(search_txt)
        )
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True
        

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.groups = []
        self.refresh_data_bindings()
        self.tb_search_group.text = None
        self.btn_clear_search.visible = False

    def super_load(self):
        superlog = TimerLogger('super_load')
        superlog.start('super_load start')
        self.data = Global.super_load
        superlog.end('super_load end')
        Global.users = self.data['users']
        Global.applicants = self.data['applicants']
