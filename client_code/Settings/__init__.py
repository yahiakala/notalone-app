from ._anvil_designer import SettingsTemplate
from anvil import *
import anvil.users
from anvil_extras import routing

from ..Global import Global


@routing.route('/settings', template='Router')
class Settings(SettingsTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.rp_mfa.add_event_handler('x-remove-mfa-id', self.remove_mfa_id)
        self.link_portal.url = Global.customer_portal
        if self.link_portal.url:
            self.link_portal.visible = True
        self.user = Global.user
        if self.user['password_hash']:
            self.cp_password.visible = True
            self.cp_mfa.visible = True
        self.rp_mfa.items = self.user['mfa']

    def btn_chg_pw_click(self, **event_args):
        self.lbl_pw_error.visible = False
        user = Global.user
        if self.tb_oldpw.text and self.tb_newpw.text:
            print('Changing password')
            try:
                anvil.users.reset_password(self.tb_oldpw.text, self.tb_newpw.text)
                self.lbl_pw_error.text = 'Password Changed!'
                self.lbl_pw_error.visible = True
                self.tb_oldpw.text = ''
                self.tb_newpw.text = ''
            except anvil.users.AuthenticationFailed:
                print('Auth failed')
                self.lbl_pw_error.text = 'Old password is incorrect.'
                self.lbl_pw_error.visible = True
            except anvil.users.PasswordNotAcceptable:
                self.lbl_pw_error.text = 'Passwords must be 8 characters or more and be harder to guess.'
                self.lbl_pw_error.visible = True
        else:
            self.lbl_pw_error.text = 'Old or new entered password is blank.'
            self.lbl_pw_error.visible = True

    def btn_add_mfa_click(self, **event_args):
        """This method is called when the button is clicked"""
        # anvil.users.mfa.configure_mfa_with_form(allow_cancel=True)
        self.configure_mfa_custom()
        # self.user = anvil.users.get_user(allow_remembered=True)
        # Global.user = self.user
        self.rp_mfa.items = self.user['mfa']

    def configure_mfa_custom(self):
        error = None
        while True:
            mfa_method, password = anvil.users.mfa._configure_mfa(self.user['email'], error, True, True, "Save")
            
            if mfa_method:
                try:
                    # anvil.users.mfa.add_mfa_method(password, mfa_method)
                    self.user = anvil.server.call('add_mfa_method', password, mfa_method)
                    alert("Your two-factor authentication configuration has been added.")
                    return True
                except anvil.users.AuthenticationFailed as e:
                    error = e.args[0]
                except Exception as e:
                    error = str(e)
            else:
                return None

    def remove_mfa_id(self, **event_args):
        """Remove a configured MFA method."""
        try:
            self.user = anvil.server.call('delete_mfa_method', event_args['password'], event_args['id'])
            Global.user = self.user
            self.rp_mfa.items = self.user['mfa']
        except anvil.users.AuthenticationFailed as e:
            alert('Password is incorrect.')