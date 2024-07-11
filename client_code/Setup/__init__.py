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
            self.img_logo.source = self.tenant['logo']
            self.tb_discord.text = self.tenant['discord_invite']
            self.rp_paypal_plans.items = self.tenant['paypal_plans']
            
            self.tenant_secrets = self.tenant_secrets or anvil.server.call('get_tenanted_data', Global.tenant_id, 'tenant_secrets')
            self.sv_discourse_api.secret = self.tenant_secrets['discourse_api_key']
            self.sv_discourse_secret.secret = self.tenant_secrets['discourse_secret']
            self.sv_paypal_client_id.secret = self.tenant_secrets['paypal_client_id']
            self.sv_paypal_secret.secret = self.tenant_secrets['paypal_secret']

    def sv_discourse_secret_reset(self, **event_args):
        with anvil.server.no_loading_indicator:
            self.sv_discourse_secret.secret = anvil.server.call('generate_secret')

    def btn_add_plan_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.add_roles:
            new_plan = {
                'name': self.tb_plan_name.text,
                'id': self.tb_plan_id.text,
                'amt': self.tb_plan_amt.text,
                'frequency': self.tb_plan_frequency.text,
                'roles': self.add_roles
            }
            self.rp_paypal_plans.items = self.tenant['paypal_plans'] + [new_plan]
            
            self.add_roles = None
        else:
            routing.alert('Please add roles to this new plan.')

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            new_tenant_data = {
                'discourse_api_key': self.sv_discourse_api.secret,
                'discourse_secret': self.sv_discourse_secret.secret,
                'paypal_client_id': self.sv_paypal_client_id.secret,
                'paypal_secret': self.sv_paypal_secret.secret,
                'name': self.tb_name.text,
                'waiver': self.tb_waiver_link.text,
                'logo': self.img_logo.source,
                'discord_invite': self.tb_discord.text,
                'paypal_plans': self.rp_paypal_plans.items
            }
            anvil.server.call('update_tenant_data', Global.tenant_id, new_tenant_data)

    def btn_plan_roles_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.add_roles = None
        
