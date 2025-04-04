import time

import anvil.users
from anvil import *
from anvil_extras import routing
from anvil_squared import utils

from ..Global import Global, AppName
from ._anvil_designer import SignupTemplate


@routing.route("signup", template="Static", url_keys=[routing.ANY])
class Signup(SignupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.user = Global.user
        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False
            self.cp_login.role = ["narrow-col", "narrow-col-mobile"]

    def route_user(self, **event_args):
        """Send the user on their way."""
        if "redirect" in self.url_dict and self.user:
            Global.user = self.user
            anvil.js.window.location.href = self.url_dict["redirect"]
        elif self.user:
            Global.user = self.user
            routing.set_url_hash("app")

    def btn_google_click(self, **event_args):
        """Signup with Google"""
        if self.user:
            self.route_user()

        try:
            self.user = anvil.users.signup_with_google(remember=True)
            self.route_user()
        except anvil.users.UserExists as e:
            anvil.alert(str(e.args[0]))
            self.user = None
            routing.set_url_hash(url_pattern="signin", url_dict=self.url_dict)

    def btn_signup_click(self, **event_args):
        """Signup with email/password"""
        if self.user:
            self.route_user()
            return

        # Disable button and show processing state
        self.btn_signup.enabled = False
        self.btn_signup.text = "Signing up..."

        # Make server call without loading indicator
        with anvil.server.no_loading_indicator:
            self.user = utils.signup_with_email(
                self.tb_email,
                self.tb_password,
                self.tb_password_repeat,
                self.lbl_error,
                AppName,
            )

        # Restore button state
        self.btn_signup.text = "Sign up"
        self.btn_signup.enabled = True

    def tb_signup_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus."""
        return utils.signup_with_email_checker(
            self.tb_email.text,
            self.tb_password.text,
            self.tb_password_repeat.text,
            self.lbl_error,
        )

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert(
            "Email support@dreambyte.ai and we'll get back to you within 24-48 hours."
        )

    def link_signin_click(self, **event_args):
        """This method is called when the link is clicked"""
        with anvil.server.no_loading_indicator:
            routing.set_url_hash(url_pattern="signin", url_dict=self.url_dict)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        time.sleep(0.5)
        self.cp_login.visible = True
