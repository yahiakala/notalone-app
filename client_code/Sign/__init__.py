from ._anvil_designer import SignTemplate
from anvil import *
import anvil.users
import time
from anvil_extras import routing

from ..Global import Global


@routing.route('', template='Static')
@routing.route('sign', template='Static', url_keys=[routing.ANY])
class Sign(SignTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.user = Global.user
        if self.user:
            routing.set_url_hash('app')

        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False
            self.cp_login.role = ['narrow-col', 'narrow-col-mobile']

    def btn_signin_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.set_url_hash(url_pattern='signin', url_dict=self.url_dict)

    def btn_signup_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.set_url_hash(url_pattern='signup', url_dict=self.url_dict)

    def form_show(self, **event_args):
        """Skip expansion animation with cp inside of fp."""
        time.sleep(0.3)
        self.fp_outer.visible = True
