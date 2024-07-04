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
        # TODO: add timer
        self.tenant = [i for i in Global.my_tenants if i['tenant_id'] == Global.tenant_id][0]
        if 'profile' in routing.get_url_pattern():
            self.user = dict(Global.user)  # Avoid errors with data bindings
            self.permissions = Global.permissions
            self.cp_booking_link.visible = True
        else:
            self.user = [i for i in Global.users if i['email'] == self.url_dict['user_email']][0]
            # self.discordlink = self.tenant['discordlink']
            self.tb_email.enabled = True
            self.cp_admin.visible = True
            self.ta_user_notes.text = self.user['notes']
            self.permissions = self.user['permissions']
            self.btn_back.visible = True

        if 'see_forum' not in self.permissions:
            self.btn_pay_new.enabled = True
        
        self.tb_email.text = self.user['email']
        self.tb_firstname.text = self.user['first_name']
        self.tb_lastname.text = self.user['last_name']
        self.tb_phone.text = self.user['phone']
        self.tb_discord_user.text = self.user['discord']
        self.link_discord.url = self.tenant['discordlink']
        self.link_codeofconduct.url = self.tenant['waiver']
        self.cb_signoff.checked = self.user['consent_check']

        self.dd_membertier.selected_value = self.user['fee']
        self.lbl_fee_paid_amt.text = self.user['fee']
        if 'see_forum' in self.permissions:
            self.cp_payment_status.visible = True

        self.tb_booking_link.text = self.user['booking_link']

        if 'see_forum' in self.permissions:
            self.cp_discord.visible = True

        if 'see_applicants' in self.permissions:
            self.cp_booking_link.visible = True

        # print('fee: ' + str(self.user['fee']))
        # Any code you write here will run before the form opens.

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        print_timestamp('memberdetail: btn_save_click')
        # TODO: separate this name alert
        if self.user["first_name"] == "" or self.user["last_name"] == "":
            self.lbl_namealert.visible = True
        else:
            self.lbl_namealert.visible = False
        print("fee: " + str(self.user["fee"]))
        Global.user = anvil.server.call("update_user", Global.tenant_id, self.user)
        self.user = dict(Global.user)

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

        fee_send = self.user["fee"]
        if not self.user["fee"]:
            fee_send = 10

        Global.user, self.payment_url = anvil.server.call("create_sub", fee_send)
        self.user = dict(Global.user)  # avoid errors with data bindings
        print("fee: " + str(self.user["fee"]))
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
        _ = anvil.server.call('reject_applicant', self.item)
        self.item['permissions'] = [i for i in self.item['permissions'] if i != 'book_interview']
        self.parent.raise_event('x-update-user', item=self.item)

    def btn_accept_applicant_click(self, **event_args):
        """This method is called when the button is clicked"""
        _ = anvil.server.call('accept_applicant', self.item)
        self.item['permissions'] = self.item['permissions'] + ['see_profile']
        self.parent.raise_event('x-update-user', item=self.item)
