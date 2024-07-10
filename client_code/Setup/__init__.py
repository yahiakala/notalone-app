from ._anvil_designer import SetupTemplate
from anvil import *
from ..Global import Global
from anvil_extras import routing



@routing.route('/admin', template='Router')
class Setup(SetupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        self.tenant = Global.tenant
        self.tb_name.text = self.tenant['name']
        self.tb_waiver_link.text = self.tenant['waiver']        
        
