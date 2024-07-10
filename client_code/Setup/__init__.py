from ._anvil_designer import SetupTemplate
from anvil import *
from ..Global import Global
from anvil_extras import routing
import anvil.server


@routing.route('/admin', template='Router')
class Setup(SetupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.tenant_secrets = None
        

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.tenant = Global.tenant
            self.tb_name.text = self.tenant['name']
            self.tb_waiver_link.text = self.tenant['waiver']
            self.tenant_secrets = self.tenant_secrets or anvil.server.call('get_tenanted_data', Global.tenant_id, 'tenant_secrets')

            self.sv_discourse_api.secret = self.tenant_secrets['discourse_api_key']
            self.sv_discourse_secret.secret = self.tenant_secrets['discourse_secret']
            self.sv_paypal_client_id.secret = self.tenant_secrets['paypal_client_id']
            self.sv_paypal_secret.secret = self.tenant_secrets['paypal_secret']

    def sv_discourse_secret_reset(self, **event_args):
        with anvil.server.no_loading_indicator:
            self.sv_discourse_secret.secret = anvil.server.call('generate_secret')
        
