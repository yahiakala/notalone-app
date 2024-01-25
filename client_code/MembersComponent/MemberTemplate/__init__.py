from ._anvil_designer import MemberTemplateTemplate
from anvil import *
import anvil.server

import datetime as dt


class MemberTemplate(MemberTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        print("Client: Getting member data binding ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.user_notes = None
        self.init_components(**properties)
        print("Client: Got member data binding ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.pmt_success = 'Member is in good standing with payments.'
        self.pmt_noid = 'Member has no linked paypal subscription.'
        self.pmt_inactive = "Member's paypal subscription is expired."
        self.lbl_payment_status.text = (
            self.pmt_success if self.item['good_standing'] else
            self.pmt_inactive if self.item['paypal_sub_id'] is not None else
            self.pmt_noid
        )
        if self.item['last_login']:
            self.lbl_last_login.text = 'Last login: ' + self.item['last_login'].strftime('%Y-%m-%d')
            self.lbl_last_login.visible = True
        if self.item['signed_up']:
            self.lbl_signed_up.text = 'Signed up: ' + self.item['signed_up'].strftime('%Y-%m-%d')
            self.lbl_signed_up.visible = True

    def btn_remove_click(self, **event_args):
        """This method is called when the button is clicked"""
        for i, j in self.item.items():
            if i.startswith('auth_'):
                self.item[i] = False
        self.refresh_data_bindings()
    
    def btn_restore_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['auth_profile'] = True
        self.item['auth_forumchat'] = True
        self.refresh_data_bindings()

    def btn_refresh_click(self, **event_args):
        """This method is called when the button is clicked"""
        print(self.item['fee'])
        self.item = anvil.server.call('check_sub', self.item)
        print(self.item['fee'])
        self.lbl_payment_status.text = (
            self.pmt_success if self.item['good_standing'] else
            self.pmt_inactive if self.item['paypal_sub_id'] is not None else
            self.pmt_noid
        )

    def btn_notes_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.cp_notes.visible:
            self.cp_notes.visible = False
        else:
            self.user_notes = anvil.server.call('get_user_notes', self.item['email'])['notes']
            self.refresh_data_bindings()
            self.cp_notes.visible = True

    def btn_save_notes_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('save_user_notes', self.item['email'], self.user_notes)

    def ta_user_notes_lost_focus(self, **event_args):
        """This method is called when the text area loses focus"""
        anvil.server.call('save_user_notes', self.item['email'], self.user_notes)

    def btn_remind_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('notify_payment', self.item)

    def btn_del_click(self, **event_args):
        """Delete user record."""
        self.cp_confirm_del.visible = True
    
    def btn_del_confirm_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.lbl_confirm_del_err.visible = False
        if self.item['email'] == self.tb_email_del_confirm.text:
            anvil.server.call('delete_user', self.item)
            self.remove_from_parent()
        else:
            self.lbl_confirm_del_err.visible = True



            






