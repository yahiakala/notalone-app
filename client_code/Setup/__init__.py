from ._anvil_designer import SetupTemplate
from anvil import *
from ..Global import Global
from anvil_extras import routing
import anvil.server
from .PlanEdit import PlanEdit
# from anvil_extras.non_blocking import call_async


@routing.route('/admin', template='Router')
class Setup(SetupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.tenant_secrets = None
        self.rp_paypal_plans.add_event_handler('x-remove-plan', self.remove_plan)
        self.rp_paypal_plans.add_event_handler('x-edit-plan', self.edit_plan)
        

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.tenant = Global.tenant
            self.tb_name.text = self.tenant['name']
            self.tb_email.text = self.tenant['email']
            self.tb_waiver_link.text = self.tenant['waiver']
            self.img_logo.source = self.tenant['logo']
            self.tb_discourse_url.text = self.tenant['discourse_url']
            self.tb_discord.text = self.tenant['discord_invite']
            self.rp_paypal_plans.items = self.tenant['paypal_plans'] or []
            
            self.tenant_secrets = self.tenant_secrets or anvil.server.call('get_tenanted_data', Global.tenant_id, 'tenant_secrets')
            self.sv_discourse_api.secret = self.tenant_secrets['discourse_api_key']
            self.sv_discourse_secret.secret = self.tenant_secrets['discourse_secret']
            self.sv_paypal_client_id.secret = self.tenant_secrets['paypal_client_id']
            self.sv_paypal_secret.secret = self.tenant_secrets['paypal_secret']
            self.sv_webhook_id.secret = self.tenant_secrets['paypal_webhook_id']

    def sv_discourse_secret_reset(self, **event_args):
        with anvil.server.no_loading_indicator:
            self.sv_discourse_secret.secret = anvil.server.call('generate_secret')

    def btn_add_plan_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_add_plan.text = 'Adding...'
        self.btn_add_plan.italic = True
        with anvil.server.no_loading_indicator:
            new_plan = routing.alert(PlanEdit(), dismissible=False, buttons=None)
            if new_plan:
                self.rp_paypal_plans.items = self.rp_paypal_plans.items + [new_plan]
        self.btn_add_plan.italic = False
        self.btn_add_plan.text = 'Add Plan'

    def edit_plan(self, item, **event_args):
        self.rp_paypal_plans.items = [i for i in self.rp_paypal_plans.items if i['id'] != item['id']] + [item]

    def remove_plan(self, item, **event_args):
        self.rp_paypal_plans.items = [i for i in self.rp_paypal_plans.items if i['id'] != item['id']]
        

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_save.text = 'Saving...'
        self.btn_save.italic = True
        with anvil.server.no_loading_indicator:
            new_tenant_data = {
                'discourse_api_key': self.sv_discourse_api.secret,
                'discourse_secret': self.sv_discourse_secret.secret,
                'paypal_client_id': self.sv_paypal_client_id.secret,
                'paypal_secret': self.sv_paypal_secret.secret,
                'paypal_webhook_id': self.sv_webhook_id.secret,
                'name': self.tb_name.text,
                'email': self.tb_email.text,
                'discourse_url': self.tb_discourse_url.text,
                'waiver': self.tb_waiver_link.text,
                'logo': self.img_logo.source,
                'discord_invite': self.tb_discord.text,
                'paypal_plans': self.rp_paypal_plans.items
            }
            anvil.server.call('update_tenant_data', Global.tenant_id, new_tenant_data)
            Global.tenant = new_tenant_data

            routerform = get_open_form()
            routerform.lbl_app_title.text = self.tb_name.text
            
        self.btn_save.italic = False
        self.btn_save.text = 'Save Changes'

    def fl_logo_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.img_logo.source = self.fl_logo.file

    def tb_waiver_link_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.validate_url(self.tb_waiver_link.text)

    def validate_url(self, url):
        if 'https://' not in url:
            routing.alert('Please enter a valid URL with https:// at the beginning')

    def tb_discourse_url_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.validate_url(self.tb_discourse_url.text)

    def tb_discord_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus"""
        self.validate_url(self.tb_discord.text)

        
