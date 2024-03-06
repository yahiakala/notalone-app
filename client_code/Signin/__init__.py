from ._anvil_designer import SigninTemplate
from anvil import *
import anvil.users
import time
from anvil_extras import routing

from .. import utils
from .. import Global


@routing.route('', template='BlankTemplate')
@routing.route('signin', template='BlankTemplate')
class Signin(SigninTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        if Global.user:
            routing.set_url_hash('app')
        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False

    

    def form_show(self, **event_args):
        time.sleep(0.3)  # Hack around weird initialization of flowpanel
        self.fp_outer.visible = True

    def btn_google_click(self, **event_args):
        """This method is called when the button is clicked"""
        user = anvil.users.login_with_google(remember=True)
        if user:
            Global.user = user
            routing.set_url_hash('app')

    def btn_signin_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.lbl_error.visible = False
        self.user = anvil.users.get_user()
        email = self.tb_email.text
        password = self.tb_password.text
        if self.user:
            utils.print_timestamp('User already logged in')
            Global.user = self.user
            routing.set_url_hash('app')
        else:
            try:
                self.user = anvil.users.login_with_email(email, password, remember=True)
                Global.user = self.user
                utils.print_timestamp('Login worked without mfa')
                routing.set_url_hash('app')
            except anvil.users.MFARequired as e:
                r = anvil.users.mfa.mfa_login_with_form(email, password)
                if r == 'reset_mfa':
                    anvil.users.mfa.send_mfa_reset_email(email)
                    self.lbl_error.text = "Requested 2-factor authentication reset for " + email + ". Check your email."
                elif r == None:
                    self.lbl_error.text = "Cancelled login."
                else:
                    self.user = anvil.users.login_with_email(email, password, mfa=r, remember=True)
                    Global.user = self.user
                    routing.set_url_hash('app')
            except anvil.users.AuthenticationFailed as e:
                self.lbl_error.text = e.args[0]
                self.lbl_error.visible = True
            except anvil.users.EmailNotConfirmed as e:
                self.lbl_error.text = "You haven't confirmed your email address. Please check your email and click the confirmation link, or reset your password."
                self.lbl_error.visible = True

    def link_forgot_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.users.send_password_reset_email(self.tb_email.text)
        self.lbl_error.text = f'please check your email ({self.tb_email.text}) for a password reset link.'

    def link_signup_click(self, **event_args):
        """This method is called when the link is clicked"""
        routing.set_url_hash('signup')
