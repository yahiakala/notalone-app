from ._anvil_designer import MembersTemplate
from anvil import *
import anvil.tables.query as q
import anvil.server

from ..Global import Global
from anvil_extras import routing
import datetime as dt
# from anvil_extras.logging import TimerLogger
from anvil_squared.utils import print_timestamp


@routing.route('/members', template='Router')
class Members(MembersTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.members = [None]
        self.populate_rp()

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.users = Global.users
            self.members = Global.users.search(
                q.fetch_only(
                    'user',
                    user=q.fetch_only(
                        'email', 'first_name', 'last_name', 'last_login', 'signed_up'
                    )
                )
            )
            self.btn_qf_applicants.enabled = True
            self.btn_qf_regular.enabled = True
            self.btn_qf_admins.enabled = True
            self.btn_qf_disabled.enabled = True
            self.btn_qf_inactive.enabled = True
            self.tb_mb_search.enabled = True
    
            if self.members is not None:
                self.populate_rp()

    def populate_rp(self, **event_args):
        self.mb_count = len(self.members)
        # self.lbl_num_results.text = str(self.mb_count) + ' result(s)'
        self.mb_count_show = min(10, self.mb_count)
        # self.rp_members.items = self.members[:self.mb_count_show]
        self.rp_members.items = self.members

    def refresh_search(self):
        """Refresh the button roles and pagination"""
        self.btn_nosub.role = 'tonal-button'
        self.btn_expiring_soon.role = 'tonal-button'
        self.btn_expired.role = 'tonal-button'
        
        self.mb_count = len(self.members)
        self.mb_count_show = min(10, self.mb_count)
        self.btn_clear_search.visible = True
        self.rp_members.items = self.members
        self.refresh_data_bindings()  # for num results label

    def tb_mb_search_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        # search_txt = '%' + self.tb_mb_search.text + '%'
        srch = self.tb_mb_search.text
        print(srch)
        # Gonna need to search through users first, then put that into an OR condition
        # in a larger query on the usermap
        self.members = [
            i for i in Global.users
            if srch in i['first_name'].lower() or srch in i['last_name'].lower() or srch in i['email'].lower() or srch in i['notes'].lower()
        ]
        self.refresh_search()

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.populate_rp()
        self.refresh_search()
        self.tb_mb_search.text = None
        self.btn_clear_search.visible = False
        
    def btn_nosub_click(self, **event_args):
        """This method is called when the button is clicked"""
        # self.members = Global.users.search(
        #     paypal_sub_id=None,
        #     fee=q.not_(0),
        #     good_standing=False
        # )
        self.members = [
            i for i in Global.users
            if i['paypal_sub_id'] is None and i['fee'] != 0 and i['good_standing'] != True
        ]
        self.refresh_search()
        self.btn_nosub.role = 'filled-button'

    def btn_expiring_soon_click(self, **event_args):
        """This method is called when the button is clicked"""
        # self.members = Global.users.search(
        #     paypal_sub_id=q.not_(None),
        #     payment_status=q.not_('ACTIVE'),
        #     fee=q.not_(0),
        #     payment_expiry=q.between(
        #         min=dt.date.today(),
        #         max=dt.date.today() + dt.timedelta(days=30),
        #         min_inclusive=True,
        #         max_inclusive=False
        #     )
        # )
        self.members = [
            i for i in Global.users
            if i['paypal_sub_id'] != None and i['payment_status'] != 'ACTIVE' and i['fee'] != 0
            and i['payment_expiry'] != None and i['payment_expiry'] >= dt.date.today()
            and i['payment_expiry'] < dt.date.today() + dt.timedelta(days=30)
        ]
        self.refresh_search()
        self.btn_expiring_soon.role = 'filled-button'

    def btn_expired_click(self, **event_args):
        """This method is called when the button is clicked"""
        # self.members = Global.users.search(
        #     paypal_sub_id=q.not_(None),
        #     payment_status=q.not_('ACTIVE'),
        #     fee=q.not_(0),
        #     payment_expiry=q.less_than(dt.date.today())
        # )
        self.members = [
            i for i in Global.users
            if i['paypal_sub_id'] != None and i['payment_status'] != 'ACTIVE' and i['fee'] != 0
            and i['payment_expiry'] != None and i['payment_expiry'] < dt.date.today()
        ]
        self.refresh_search()
        self.btn_expired.role = 'filled-button'

    def btn_qf_admins_click(self, **event_args):
        """People on the $10 tier with no role."""
        self.members = [
            i for i in Global.users
            if i['good_standing'] and i['fee'] == 10 and not i['roles']
        ]
        self.refresh_search()
        self.btn_norole.role = 'filled-button'

    def btn_qf_applicants_click(self, **event_args):
        """This method is called when the button is clicked"""
        # TODO: apply filters
        self.rp_members.items = [
            i for i in self.members
            if 'book_interview' in i['permissions']
        ]
        self.btn_clear_search.visible = True

    def btn_qf_inactive_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.rp_members.items = [
            i for i in self.members
            if 'see_profile' not in i['permissions']
            and 'book_interview' not in i['permissions']
        ]
        self.btn_clear_search.visible = True

    def apply_filters(self, **event_args):
        pass
        # enable to check if ONLY one role or ONLY certain permissions


