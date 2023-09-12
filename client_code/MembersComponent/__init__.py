from ._anvil_designer import MembersComponentTemplate
from anvil import *
import anvil.tables.query as q

from .. import Global

import datetime as dt


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
        self.members = Global.users.search()
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)

    def btn_show_more_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.mb_count_show = min(self.mb_count_show + 5, self.mb_count)
        self.refresh_data_bindings()
        self.btn_show_more.scroll_into_view()

    def refresh_search(self):
        self.btn_nosub.role = 'tonal-button'
        self.btn_expiring_soon.role = 'tonal-button'
        self.btn_expired.role = 'tonal-button'
        
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True

    def tb_mb_search_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        search_txt = '%' + self.tb_mb_search.text + '%'
        self.members = Global.users.search(
            q.any_of(
                first_name=q.ilike(search_txt),
                last_name=q.ilike(search_txt),
                email=q.ilike(search_txt)
            )
        )
        self.refresh_search()

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.populate_rp()
        self.refresh_search()
        self.tb_mb_search.text = None
        self.btn_clear_search.visible = False
        
    def btn_nosub_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(
            paypal_sub_id=None,
            fee=q.not_(0),
            auth_forumchat=True
        )
        self.refresh_search()
        self.btn_nosub.role = 'filled-button'

    def btn_expiring_soon_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(
            paypal_sub_id=q.not_(None),
            payment_status=q.not_('ACTIVE'),
            fee=q.not_(0),
            payment_expiry=q.between(
                min=dt.date.today(),
                max=dt.date.today() + dt.timedelta(days=30),
                min_inclusive=True,
                max_inclusive=False
            ),
            auth_forumchat=True
        )
        self.refresh_search()
        self.btn_expiring_soon.role = 'filled-button'

    def btn_expired_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(
            paypal_sub_id=q.not_(None),
            payment_status=q.not_('ACTIVE'),
            fee=q.not_(0),
            auth_forumchat=True,
            payment_expiry=q.less_than(dt.date.today())
        )
        self.refresh_search()
        self.btn_expired.role = 'filled-button'





