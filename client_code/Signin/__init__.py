import time

import anvil.server
import anvil.users
from anvil import *
from anvil_extras import routing
from anvil_squared import utils

from ..Global import Global
from ._anvil_designer import SigninTemplate


@routing.route("signin", template="Static", url_keys=[routing.ANY])
class Signin(SigninTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.user = Global.user
        self.route_user()

        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False
            self.cp_login.role = ["narrow-col", "narrow-col-mobile"]

    def route_user(self, **event_args):
        """Send the user on their way."""
        if "redirect" in self.url_dict and self.user:
            self.tb_email.text = ""
            self.tb_password.text = ""
            Global.user = self.user
            anvil.js.window.location.href = self.url_dict["redirect"]
        elif self.user:
            self.tb_email.text = ""
            self.tb_password.text = ""
            Global.user = self.user
            routing.set_url_hash("app")

    def btn_google_click(self, **event_args):
        """Signin with google. Creates a user if none exists."""
        with anvil.server.no_loading_indicator:
            self.btn_google.text = "Signing in..."
            self.btn_google.italic = True
            self.user = anvil.users.login_with_google(remember=True)
            self.route_user()
            self.btn_google.text = "Sign in with Google"
            self.btn_google.italic = False

    def link_forgot_click(self, **event_args):
        """This method is called when the link is clicked"""
        utils.reset_password(self.tb_email, self.lbl_error)

    def link_signup_click(self, **event_args):
        """This method is called when the link is clicked"""
        with anvil.server.no_loading_indicator:
            routing.set_url_hash(url_pattern="signup", url_dict=self.url_dict)

    def btn_signin_click_custom(self, **event_args):
        # Disable button and show processing state
        self.btn_signin.enabled = False
        self.btn_signin.text = "Signing in..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            self.user = utils.signin_with_email(
                self.tb_email, self.tb_password, self.lbl_error
            )
            self.route_user()

        # Restore button state
        self.btn_signin.text = "Sign in"
        self.btn_signin.enabled = True

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert(
            "Email support@dreambyte.ai and we'll get back to you within 24-48 hours."
        )

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        time.sleep(0.5)
        self.cp_login.visible = True
