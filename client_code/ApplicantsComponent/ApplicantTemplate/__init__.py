from ._anvil_designer import ApplicantTemplateTemplate
from anvil import *
import anvil.server
from ... import Global

class ApplicantTemplate(ApplicantTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user_notes = None
        self.user = Global.user
        self.init_components(**properties)
        self.user_notes = self.item['notes']
        self.refresh_data_bindings()

    def btn_accept_click(self, **event_args):
        """This method is called when the button is clicked"""
        _ = anvil.server.call('reassign_roles', self.item, {'auth_profile': True, 'auth_booking': False})
        anvil.server.call('notify_accept', self.item['email'])
        self.parent.raise_event('x-refresh')

    def btn_reject_click(self, **event_args):
        """Just remove their ability to book another screening."""
        _ = anvil.server.call('reassign_roles', self.item, {'auth_booking': False})
        self.parent.raise_event('x-refresh')

    def ta_notes_lost_focus(self, **event_args):
        """This method is called when the text area loses focus"""
        anvil.server.call('save_user_notes', self.item['email'], self.user_notes)

    def btn_save_notes_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.user_notes:
            anvil.server.call('save_user_notes', self.item['email'], self.user_notes)

    def btn_del_click(self, **event_args):
        """Delete user record."""
        self.cp_confirm_del.visible = True
    
    def btn_del_confirm_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.lbl_confirm_del_err.visible = False
        if self.item['email'] == self.tb_email_del_confirm.text:
            anvil.server.call('delete_user', self.item)
            self.parent.raise_event('x-refresh')
        else:
            self.lbl_confirm_del_err.visible = True

    def btn_showhide_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.cp_notes.visible:
            self.cp_notes.visible = False
        else:
            self.cp_notes.visible = True

