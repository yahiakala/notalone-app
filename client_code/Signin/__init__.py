from ._anvil_designer import SigninTemplate
from anvil import *
import anvil.users
# import time
from anvil_extras import routing
from anvil_squared import utils

from ..Global import Global


@routing.route('signin', template='Static', url_keys=[routing.ANY])
class Signin(SigninTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.user = Global.user
        self.route_user()

        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False
            self.cp_login.role = ['narrow-col', 'narrow-col-mobile']

    def route_user(self, **event_args):
        """Send the user on their way."""
        if 'redirect' in self.url_dict and self.user:
            self.tb_email.text = ''
            self.tb_password.text = ''
            Global.user = self.user
            anvil.js.window.location.href = self.url_dict['redirect']
        elif self.user:
            self.tb_email.text = ''
            self.tb_password.text = ''
            Global.user = self.user
            routing.set_url_hash('app')
    
    def btn_google_click(self, **event_args):
        """Signin with google. Creates a user if none exists."""
        self.user = anvil.users.login_with_google(remember=True)
        self.route_user()

    def link_forgot_click(self, **event_args):
        """This method is called when the link is clicked"""
        utils.reset_password(self.tb_email, self.lbl_error)

    def link_signup_click(self, **event_args):
        """This method is called when the link is clicked"""
        routing.set_url_hash(url_pattern='signup', url_dict=self.url_dict)

    def btn_signin_click_custom(self, **event_args):
        self.user = utils.signin_with_email(
            self.tb_email, self.tb_password,
            'login_with_email_custom', self.lbl_error
        )
        self.route_user()

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert("Email support@dreambyte.ai and we'll get back to you within 24-48 hours.")