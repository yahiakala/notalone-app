from ._anvil_designer import RoleRowTemplate
from anvil import *
from anvil_extras import routing
from ...Global import Global


class RoleRow(RoleRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        if self.item:
            self.lbl_name.text = self.item['name']
            self.lbl_last_update.text = self.item['last_update']
            self.lbl_name.role = None
            self.lbl_last_update.role = None
            
    def btn_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.set_url_hash(url_pattern='app/roledetail', url_dict={'role': self.item['name']})

    def btn_members_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.set_url_hash(
            url_pattern='app/members',
            url_dict={'role': self.item['name']}
        )


