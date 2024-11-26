from ._anvil_designer import MemberDetailTemplate
from anvil import *
import anvil.server
from anvil_extras import routing
from ..Global import Global
from .PriceCard import PriceCard
from anvil_squared.utils import print_timestamp


@routing.route("/memberdetail", template="Router", url_keys=['user_email'])
@routing.route('/profile', template='Router')
class MemberDetail(MemberDetailTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        if 'memberdetail' in routing.get_url_pattern():
            self.btn_back.visible = True
        self.fp_pricing_table.add_event_handler('x-pay-click', self.pay_click)
    
    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.load_data()

    def load_data(self):
        if 'profile' in routing.get_url_pattern():
            self.email = Global.user['email']
            self.cp_booking_link.visible = True
        else:
            self.email = self.url_dict['user_email']
            self.cp_admin.visible = True
            if 'edit_members' not in Global.permissions:
                self.tb_firstname.enabled = False
                self.tb_lastname.enabled = False
                self.tb_phone.enabled = False
                self.tb_discord_user.enabled = False
                self.cb_signoff.enabled = False
                self.tb_booking_link.enabled = False
                self.btn_save.visible = False
                self.msc_roles.visible = False
                self.btn_del.visible = False

        self.member = anvil.server.call('get_member_data', Global.tenant_id, self.email)
        self.populate_role_list()
        self.ta_user_notes.text = self.member['notes']

        if 'Applicant' in self.member['roles']:
            self.btn_accept_applicant.visible = True 
            self.btn_reject_applicant.visible = True
        
        self.tb_email.text = self.email
        self.tb_firstname.text = self.member['first_name']
        self.tb_lastname.text = self.member['last_name']
        self.tb_phone.text = self.member['phone']
        self.tb_discord_user.text = self.member['discord']
        self.link_discord.url = Global.tenant['discord_invite']
        self.link_codeofconduct.url = Global.tenant['waiver']
        self.cb_signoff.checked = self.member['consent_check']

        self.lbl_fee_paid_amt.text = self.member['fee']
        if 'see_forum' in self.member['permissions']:
            self.cp_discord.visible = True
            

        if self.member['payment_status']:
            self.lbl_sub_status.visible = True 
            self.lbl_sub_status_value.visible = True 
            self.lbl_sub_status_value.text = self.member['payment_status']

        if self.member['fee']:
            self.lbl_fee_paid.visible = True 
            self.lbl_fee_paid_amt.visible = True
            self.lbl_fee_paid_amt.text = self.member['fee']

        if self.member['payment_expiry'] and self.member['payment_status']:
            self.lbl_next_payment.visible = True 
            self.lbl_next_payment_value.visible = True
            self.lbl_next_payment_value.text = self.member['payment_expiry'].strftime('%Y-%m-%d')
            if self.member['payment_status'] != 'ACTIVE':
                self.lbl_next_payment.text = 'Membership Expiry Date:'
            
        if self.member['paypal_sub_id'] and self.member['payment_status'] == 'ACTIVE':
            self.btn_cancel_sub.visible = True

        self.tb_booking_link.text = self.member['booking_link']

        if 'see_members' in self.member['permissions']:
            self.cp_booking_link.visible = True

        self.tb_email.role = 'outlined'
        self.tb_firstname.role = 'outlined'
        self.tb_lastname.role = 'outlined'
        self.tb_phone.role = 'outlined'

        self.ta_user_notes.role = 'outlined'
        self.tb_discord_user.role = 'outlined'
        self.lbl_fee_paid_amt.role = None
        self.tb_booking_link.role = 'outlined'

        if self.member['payment_status'] != 'ACTIVE' and 'profile' in routing.get_url_pattern():
            for plan in Global.tenant['paypal_plans']:
                self.fp_pricing_table.add_component(PriceCard(item=plan))
            self.fp_pricing_table.visible = True
    
    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        print_timestamp('memberdetail: btn_save_click')

        self.btn_save.text = 'Saving...'
        self.btn_save.italic = True
        
        with anvil.server.no_loading_indicator:
            if self.tb_firstname.text == "" or self.tb_lastname.text == "":
                self.lbl_namealert.visible = True
            else:
                self.lbl_namealert.visible = False
            
            self.member['first_name'] = self.tb_firstname.text
            self.member['last_name'] = self.tb_lastname.text
            self.member['phone'] = self.tb_phone.text
            self.member['discord'] = self.tb_discord_user.text
            self.member['booking_link'] = self.tb_booking_link.text
            self.member['consent_check'] = self.cb_signoff.checked
            
            if 'memberdetail' in routing.get_url_pattern() and 'edit_members' in Global.permissions:
                print(self.msc_roles.selected)
                self.member['roles'] = [i['key'] for i in self.msc_roles.selected]
                print_timestamp('roles at save')
                print(self.member['roles'])
                self.member['notes'] = self.ta_user_notes.text

            self.member = anvil.server.call(
                'edit_member',
                Global.tenant_id,
                self.member,
            )
            routing.clear_cache()

        self.btn_save.italic = False
        self.btn_save.text = 'Save all changes'

    def btn_cancel_sub_click(self, **event_args):
        """This method is called when the cancel subscription button is clicked"""
        if alert("Are you sure you want to cancel this subscription?", buttons=["Yes", "No"]) == "Yes":
            self.btn_cancel_sub.text = "Cancelling..."
            self.btn_cancel_sub.enabled = False
            
            with anvil.server.no_loading_indicator:
                # try:
                self.member = anvil.server.call('cancel_user_subscription', Global.tenant_id, self.email)
                self.btn_cancel_sub.visible = False
                self.lbl_fee_paid_copy.text = "Subscription cancelled but membership still in good standing."
                alert("Subscription cancelled successfully")
                # except Exception as e:
                #     alert(str(e))
                #     self.btn_cancel_sub.text = "Cancel Subscription"
                #     self.btn_cancel_sub.enabled = True

    def pay_click(self, item, **event_args):
        """This method is called when the button is clicked"""
        print_timestamp('memberdetail: pay_click')
        from anvil.js import window

        with anvil.server.no_loading_indicator:
            self.member, self.payment_url = anvil.server.call("create_sub", Global.tenant_id, item['id'])
            self.btn_save_click()
            routing.clear_cache()
            window.location.href = self.payment_url  # same window

    def btn_back_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.go_back()

    def btn_reject_applicant_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.member = anvil.server.call('reject_applicant', Global.tenant_id, self.email)
        self.populate_role_list()
        routing.clear_cache()
        self.btn_accept_applicant.visible = False
        self.btn_reject_applicant.visible = False
        
    def btn_accept_applicant_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.member = anvil.server.call('accept_applicant', Global.tenant_id, self.email)
        self.populate_role_list()
        routing.clear_cache()
        self.btn_accept_applicant.visible = False
        self.btn_reject_applicant.visible = False

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
            if 'see_members' in Global.permissions:
                anvil.server.call(
                    'save_user_notes',
                    Global.tenant_id,
                    self.email,
                    self.ta_user_notes.text
                )
                self.member['notes'] = self.ta_user_notes.text
                
        self.btn_save_notes.italic = False
        self.btn_save_notes.text = 'Save Notes'

    def populate_role_list(self):
        self.all_roles = [i['name'] for i in Global.roles]
        self.msc_roles.items = [
            {
                'key': i['name'],
                'value': i['name'],
                'description': i['name']
            }
            for i in Global.roles
        ]
        self.msc_roles.selected = [
            {
                'key': i,
                'value': i,
                'description': i
            }
            for i in self.member['roles']
        ]

    def btn_test_email_click(self, **event_args):
        """This method is called when the button is clicked"""
        anvil.server.call('send_test_email', Global.tenant_id, self.email)

    def btn_refresh_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_refresh.enabled = False
        self.btn_refresh.text = 'Refreshing...'
        self.btn_refresh.italic = True
        
        with anvil.server.no_loading_indicator:
            try:
                self.member = anvil.server.call('refresh_subscription_data', Global.tenant_id, self.email)
                routing.reload_page(hard=True)
            except Exception as e:
                if 'No active subscription found' in str(e):
                    alert('No active subscription found.')
                else:
                    raise
        self.btn_refresh.italic = False
        self.btn_refresh.text = 'Refresh'
        self.btn_refresh.enabled = True
