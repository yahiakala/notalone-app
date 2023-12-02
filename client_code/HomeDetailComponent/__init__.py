from ._anvil_designer import HomeDetailComponentTemplate
from anvil import *
import anvil.tables.query as q

from .. import Global

class HomeDetailComponent(HomeDetailComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.groups = []
        self.user = Global.user
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        self.rp_groups.add_event_handler('x-refresh', self.update_stuff)
        self.link_1.url = Global.forumlink

    def update_stuff(self, **event_args):
        self.groups = []
        self.user = Global.user
        self.refresh_data_bindings()
        self.raise_event('x-refresh')

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

