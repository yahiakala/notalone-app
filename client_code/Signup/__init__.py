from ._anvil_designer import SignupTemplate
from anvil import *
import anvil.users
from anvil_extras import routing

from .. import utils
from .. import Global


@routing.route('signup', template='BlankTemplate')
class Signup(SignupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.spacer_1.visible = False

    def btn_google_click(self, **event_args):
        """This method is called when the button is clicked"""
        try:
            user = anvil.users.signup_with_google(remember=True)
        except anvil.users.UserExists as e:
            anvil.alert(str(e.args[0]))
            user = None
            routing.set_url_hash('signin')
        
        if user:
            Global.user = user
            routing.set_url_hash('homedetail')

    def btn_signup_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.lbl_error.visible = False
        self.user = None
        email = self.tb_email.text
        password = self.tb_password.text
        proceed = self.tb_password_repeat_lost_focus()
        if proceed:
            try:
                self.user = anvil.users.signup_with_email(email, password, remember=True)
            except anvil.users.MFARequired:
                mfa_method, _ = anvil.users.mfa._configure_mfa(email, None, False, [("Cancel", None)], "Sign up")
                self.user = anvil.server.call("anvil.private.users.signup_with_email", email, password, mfa_method=mfa_method, remember=True)
            except anvil.users.UserExists as e:
                self.lbl_error.text = str(e.args[0])
                self.lbl_error.visible = True
            except anvil.users.PasswordNotAcceptable as e:
                self.lbl_error.text = str(e.args[0])
                self.lbl_error.visible = True
    
        if self.user:
            self.tb_email.text = ''
            self.tb_password.text = ''
            self.tb_password_repeat.text = ''
            self.lbl_error.text = (
                "We've sent a confirmation email to " + email + ". Open your inbox and click the link to complete your signup."
            )
            self.lbl_error.visible = True

    def tb_password_repeat_lost_focus(self, **event_args):
        """This method is called when the TextBox loses focus."""
        if len(self.tb_email.text) < 5 or "@" not in self.tb_email.text or "." not in self.tb_email.text:
            self.lbl_error.text = "Enter an email address"
        elif self.tb_password.text == '' or self.tb_password.text is None:
            self.lbl_error.text = 'Please enter a password.'
        elif self.tb_password_repeat.text != self.tb_password.text:
            self.lbl_error.text = 'Passwords do not match.'
        else:
            self.lbl_error.visible = False
            return True

        self.lbl_error.visible = True
        return False