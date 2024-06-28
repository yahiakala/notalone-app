from ._anvil_designer import MembersComponentTemplate
from anvil import *
import anvil.tables.query as q
import anvil.server

from ..Global import Global
from anvil_extras import routing
import datetime as dt
from anvil_extras.logging import TimerLogger


@routing.route('/members', template='Router')
class MembersComponent(MembersComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        # print("Client: Getting members ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        # self.members = Global.users.search(auth_profile=True)
        # print("Client: Got members ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.populate_rp()
        self.init_components(**properties)
        # self.payment_exempt = [['screener', 'leader']]

        # self.rp_members.add_event_handler('x-refresh', self.populate_rp)

    def populate_rp(self, **event_args):
        t_get_users = TimerLogger('get_users timing')
        t_get_users.start('starting get_users')
        self.members = Global.users
        t_get_users.check('got users')
        self.mb_count = len(self.members)
        self.mb_count_show = min(10, self.mb_count)
        self.rp_members.items = self.members[:self.mb_count_show]
        t_get_users.end('populated repeating panel')

    def btn_show_more_click(self, **event_args):
        """This method is called when the button is clicked"""
        curr_pos = self.mb_count_show
        self.mb_count_show = min(self.mb_count_show + 10, self.mb_count)
        self.rp_members.items = self.members[:self.mb_count_show]
        curr_item = self.rp_members.get_components()[curr_pos-1]
        curr_item.scroll_into_view(smooth=False)
        self.refresh_data_bindings()

    def refresh_search(self):
        """Refresh the button roles and pagination"""
        self.btn_nosub.role = 'tonal-button'
        self.btn_expiring_soon.role = 'tonal-button'
        self.btn_expired.role = 'tonal-button'
        
        self.mb_count = len(self.members)
        self.mb_count_show = min(10, self.mb_count)
        self.btn_clear_search.visible = True
        self.rp_members.items = self.members[:self.mb_count_show]
        self.refresh_data_bindings()  # for num results label

    def tb_mb_search_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        # search_txt = '%' + self.tb_mb_search.text + '%'
        srch = self.tb_mb_search.text
        print(srch)
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

    def btn_norole_click(self, **event_args):
        """People on the $10 tier with no role."""
        self.members = [
            i for i in Global.users
            if i['good_standing'] and i['fee'] == 10 and not i['roles']
        ]
        self.refresh_search()
        self.btn_norole.role = 'filled-button'





