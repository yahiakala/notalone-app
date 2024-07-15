from ._anvil_designer import RoleDetailTemplate
from anvil import *
import anvil.server
from anvil_extras import routing


@routing.route('/roledetail', template='Router', url_keys=['role'])
class RoleDetail(RoleDetailTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def fl_add_file_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.fl_add_file.text = 'Uploading...'
        self.fl_add_file.italic = True
        with anvil.server.no_loading_indicator:
            pass
