from ._anvil_designer import ProfileComponentTemplate
from anvil import *
import anvil.server
from anvil_extras import routing
from ..Global import Global


@routing.route('/profile', template='Router')
class ProfileComponent(ProfileComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = dict(Global.user)  # Avoid errors with data bindings
        self.discordlink = Global.discordlink
        self.init_components(**properties)
        # print('fee: ' + str(self.user['fee']))
        # Any code you write here will run before the form opens.

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.user['first_name'] == '' or self.user['last_name'] == '':
            self.lbl_namealert.visible = True
        else:
            self.lbl_namealert.visible = False
        print('fee: ' + str(self.user['fee']))
        Global.user = anvil.server.call('update_user', Global.tenant_id, self.user)
        self.user = dict(Global.user)

    def tb_donation_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.link_payment.url = (
            '' if not self.tb_donation.text
            else self.lbl_10 if self.tb_donation.text < 50
            else self.lbl_50
        )

    def btn_pay_new_click(self, **event_args):
        """This method is called when the button is clicked"""
        from anvil.js import window
        fee_send = self.user['fee']
        if not self.user['fee']:
            fee_send = 10

        Global.user, self.payment_url = anvil.server.call(
            'create_sub', fee_send
        )
        self.user = dict(Global.user)  # avoid errors with data bindings
        print('fee: ' + str(self.user['fee']))
        self.btn_save_click()
        # window.open(self.payment_url)
        window.location.href = self.payment_url  # same window
        self.refresh_data_bindings()
        routing.set_url_hash('homedetail', load_from_cache=False)



