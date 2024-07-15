from ._anvil_designer import RoleDetailTemplate
from anvil import *
import anvil.server
# import anvil.http
from anvil_extras import routing
from ..Global import Global


@routing.route('/roledetail', template='Router', url_keys=['role'])
class RoleDetail(RoleDetailTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.rp_files.items = [None, None, None]
        
    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        print(self.url_dict['role'])
        # print(anvil.http.decode(self.url_dict['role']))
        self.item = [i for i in Global.roles if i['name'] == self.url_dict['role']][0]

        self.tb_name.text = self.item['name']
        self.msdd_permissions.items = Global.all_permissions
        self.msdd_permissions.selected = self.item['permissions']
        
        self.tb_name.role = 'outlined'
        if self.item['can_edit']:
            self.tb_name.enabled = True
            # self.msdd_permissions.enabled = True
            self.rp_files.items = self.item['guides']
            self.rp_files.visible = True
            self.fl_add_file.visible = True
        else:
            self.tb_name.enabled = False
            # self.msdd_permissions.enabled = False
        
    def fl_add_file_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.fl_add_file.text = 'Uploading...'
        self.fl_add_file.italic = True
        with anvil.server.no_loading_indicator:
            pass
            self.rp_files.items = ''

    def btn_back_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.go_back()

    def msdd_permissions_change(self, **event_args):
        """This method is called when the selected values change"""
        if 'edit_roles' in Global.permissions:
            pass


            