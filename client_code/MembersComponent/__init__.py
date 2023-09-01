from ._anvil_designer import MembersComponentTemplate
from anvil import *
import anvil.tables.query as q

from .. import Global

import datetime as dt


class MembersComponent(MembersComponentTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        print("Client: Getting members ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.members = Global.users.search(roles=['member'])
        print("Client: Got members ", dt.datetime.now().strftime("%H:%M:%S.%f"))
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)
        self.init_components(**properties)
        self.payment_exempt = [['screener', 'leader']]

        self.rp_members.add_event_handler('x-refresh1', self.update_stuff)

    def update_stuff(self, **event_args):
        self.members = Global.users.search(roles=['member'])
        self.refresh_data_bindings()

    def btn_show_more_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.mb_count_show = min(self.mb_count_show + 5, self.mb_count)
        self.refresh_data_bindings()
        self.btn_show_more.scroll_into_view()

    def tb_mb_search_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        search_txt = '%' + self.tb_mb_search.text + '%'
        self.members = Global.users.search(
            q.any_of(
                first_name=q.ilike(search_txt),
                last_name=q.ilike(search_txt),
                email=q.ilike(search_txt)
            ),
            roles=['member']
        )
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(roles=['member'])
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)
        self.refresh_data_bindings()
        self.tb_mb_search.text = None
        self.btn_clear_search.visible = False
        self.btn_nosub.role = 'tonal-button'
        self.btn_notactive.role = 'tonal-button'

    def btn_notactive_click(self, **event_args):
        """This method is called when the button is clicked"""
        # TODO: deprecated
        self.members = Global.users.search(
            paypal_sub_id=q.not_(None),
            payment_enrolled=False,
            fee=q.not_(0),
            roles=['member']
        )
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True
        self.btn_notactive.role = 'filled-button'

    def btn_nosub_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(
            paypal_sub_id=None,
            fee=q.not_(0),
            roles=['member']
        )
        self.mb_count = len(self.members)
        self.mb_count_show = min(5, self.mb_count)
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True
        self.btn_nosub.role = 'filled-button'

    def btn_expiring_soon_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass

    def btn_expired_click(self, **event_args):
        """This method is called when the button is clicked"""
        pass





