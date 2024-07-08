from ._anvil_designer import MemberDetailTemplate
from anvil import *
import anvil.server
from anvil_extras import routing
from ..Global import Global
from anvil_squared.utils import print_timestamp


@routing.route("/memberdetail", template="Router", url_keys=['user_email'])
@routing.route('/profile', template='Router')
class MemberDetail(MemberDetailTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        if 'memberdetail' in routing.get_url_pattern():
            self.btn_back.visible = True

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        print_timestamp('memberdetail: btn_save_click')

        self.btn_save.text = 'Saving...'
        self.btn_save.italic = True
        
        with anvil.server.no_loading_indicator:
            if self.usermap["first_name"] == "" or self.usermap["last_name"] == "":
                self.lbl_namealert.visible = True
            else:
                self.lbl_namealert.visible = False
            print("fee: " + str(self.usermap["fee"]))
    
            if 'profile' in routing.get_url_pattern() or 'edit_members' in Global.permissions:
                self.usermap['first_name'] = self.tb_firstname.text
                self.usermap['last_name'] = self.tb_lastname.text
                self.usermap['phone'] = self.tb_phone.text
                self.usermap['discord'] = self.tb_discord_user.text
                self.usermap['booking_link'] = self.tb_booking_link.text

        self.btn_save.italic = False
        self.btn_save.text = 'Save all changes'

    def tb_donation_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        self.link_payment.url = (
            ""
            if not self.tb_donation.text
            else self.lbl_10
            if self.tb_donation.text < 50
            else self.lbl_50
        )

    def btn_pay_new_click(self, **event_args):
        """This method is called when the button is clicked"""
        print_timestamp('memberdetail: btn_pay_new_click')
        from anvil.js import window

        fee_send = self.usermap["fee"]
        if not self.usermap["fee"]:
            fee_send = 10

        Global.user, self.payment_url = anvil.server.call("create_sub", fee_send)
        self.user = dict(Global.user)  # avoid errors with data bindings
        print("fee: " + str(self.usermap["fee"]))
        self.btn_save_click()
        # window.open(self.payment_url)
        window.location.href = self.payment_url  # same window
        self.refresh_data_bindings()
        routing.set_url_hash("homedetail", load_from_cache=False)

    def btn_back_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.go_back()

    def btn_reject_applicant_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.usermap = anvil.server.call('reject_applicant', Global.tenant_id, self.email)
        self.roles = self.get_roles(self.usermap)
        self.permissions = self.get_permissions(self.usermap)
        
    def btn_accept_applicant_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.usermap = anvil.server.call('accept_applicant', Global.tenant_id, self.email)
        self.roles = self.get_roles(self.usermap)
        self.permissions = self.get_permissions(self.usermap)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.load_data()

    def load_data(self):
        self.tenant = [i for i in Global.my_tenants if i['tenant_id'] == Global.tenant_id][0]
        if 'profile' in routing.get_url_pattern():
            self.usermap = Global.my_usermap
            self.permissions = Global.permissions
            self.cp_booking_link.visible = True
            self.email = Global.user['email']
        else:
            if 'edit_members' in Global.permissions:
                self.usermap = anvil.server.call('get_user_by_email_writable', Global.tenant_id, self.url_dict['user_email'])
            elif 'see_members' in Global.permissions:
                self.usermap = anvil.server.call('get_user_by_email', Global.tenant_id, self.url_dict['user_email'])
            else:
                raise anvil.server.PermissionDenied('You do not have permission to see this.')

            self.permissions = self.get_permissions(self.usermap)
            self.email = self.url_dict['user_email']
            self.cp_admin.visible = True
            self.ta_user_notes.text = self.usermap['notes']

        if 'see_forum' not in self.permissions:
            self.btn_pay_new.enabled = True
        
        self.tb_email.text = self.email
        self.tb_firstname.text = self.usermap['first_name']
        self.tb_lastname.text = self.usermap['last_name']
        self.tb_phone.text = self.usermap['phone']
        self.tb_discord_user.text = self.usermap['discord']
        self.link_discord.url = self.tenant['discordlink']
        self.link_codeofconduct.url = self.tenant['waiver']
        self.cb_signoff.checked = self.usermap['consent_check']

        self.dd_membertier.selected_value = self.usermap['fee']
        self.lbl_fee_paid_amt.text = self.usermap['fee']
        if 'see_forum' in self.permissions:
            self.cp_payment_status.visible = True

        self.tb_booking_link.text = self.usermap['booking_link']

        if 'see_forum' in self.permissions:
            self.cp_discord.visible = True

        if 'see_applicants' in self.permissions:
            self.cp_booking_link.visible = True

        self.tb_email.role = 'outlined'
        self.tb_firstname.role = 'outlined'
        self.tb_lastname.role = 'outlined'
        self.tb_phone.role = 'outlined'

        self.ta_user_notes.role = 'outlined'
        self.tb_discord_user.role = 'outlined'
        self.lbl_fee_paid_amt.role = None
        self.tb_booking_link.role = 'outlined'

    def get_user_readable(self):
        self.usermap = anvil.server.call('get_user_by_email', Global.tenant_id, self.url_dict['user_email'])
        self.permissions = self.get_permissions(self.usermap)

    def get_user_writable(self):
        self.usermap = anvil.server.call('get_user_by_email_writable', Global.tenant_id, self.url_dict['user_email'])
        self.permissions = self.get_permissions(self.usermap)

    def get_permissions(self, usermap):
        user_permissions = []
        if usermap['roles']:
            for role in usermap['roles']:
                if role['permissions']:
                    for permission in role['permissions']:
                        user_permissions.append(permission['name'])
        return list(set(user_permissions))

    def btn_del_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('delete_user', Global.tenant_id, self.email)
        Global.users = None
        routing.clear_cache()
        routing.go_back()

    def btn_save_notes_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_save_notes.text = 'Saving...'
        self.btn_save_notes.italic = True
        with anvil.server.no_loading_indicator:
            if 'edit_members' in Global.permissions:
                self.usermap['notes'] = self.ta_user_notes.text
            else:
                anvil.server.call(
                    'save_user_notes',
                    Global.tenant_id,
                    self.email,
                    self.ta_user_notes.text
                )
        self.btn_save_notes.italic = False
        self.btn_save_notes.text = 'Save Notes'
        