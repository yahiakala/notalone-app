from ._anvil_designer import MemberTemplateTemplate
from anvil import *
import anvil.server

import datetime as dt
from ...Global import Global


class MemberTemplate(MemberTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        print("Client: Getting member data binding ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.init_components(**properties)
        if self.item:
            self.lbl_name.text = self.item['first_name'] + ' ' + self.item['last_name'] + ' (' + self.item['email'] + ')'
            self.lbl_fb_url.text = 'Facebook: ' + self.item['fb_url']
            self.lbl_discord_user.text = 'Discord: ' + self.item['discord']
            self.lbl_payment_tier.text = 'Payment Tier: ' + str(self.item['fee'])
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
            self.ta_user_notes.text = self.item['notes']

            self.btn_remove.visible = True if 'see_forum' in self.item['permissions'] else False
            self.btn_restore.visible = False if 'see_forum' in self.item['permissions'] else True
            self.btn_remind.visible = False if 'see_forum' in self.item['permissions'] else True

        else:
            self.img_load.visible = True

    def btn_remove_click(self, **event_args):
        """This method is called when the button is clicked"""
        for i, j in self.item.items():
            if i.startswith('auth_'):
                self.item[i] = False
        self.refresh_data_bindings()
    
    def btn_restore_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.item['auth_profile'] = True
        # self.item['auth_forumchat'] = True
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
            self.cp_notes.visible = True
        self.refresh_data_bindings()
        print(self.item['notes'])

    def btn_save_notes_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('save_user_notes', Global.tenant_id, self.item['email'], self.ta_user_notes.text)

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

    def cb_members_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        _ = anvil.server.call('update_member', self.item['email'],
                              {'auth_members': self.item['auth_members']})

    def cb_screenings_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        _ = anvil.server.call('update_member', self.item['email'],
                              {'auth_screenings': self.item['auth_screenings']})

    def cb_forumchat_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        _ = anvil.server.call('update_member', self.item['email'],
                              {'auth_forumchat': self.item['auth_forumchat']})

    def cb_profile_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        _ = anvil.server.call('update_member', self.item['email'],
                              {'auth_profile': self.item['auth_profile']})

    def cb_authbooking_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        _ = anvil.server.call('update_member', self.item['email'],
                              {'auth_booking': self.item['auth_booking']})



            






