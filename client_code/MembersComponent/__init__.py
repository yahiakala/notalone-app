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
        self.mb_count_show = min(10, self.mb_count)
        self.rp_members.items = self.members[:self.mb_count_show]
        self.init_components(**properties)

        self.rp_members.add_event_handler('x-refresh1', self.update_stuff)

    def update_stuff(self, **event_args):
        self.members = Global.users.search(roles=['member'])
        self.refresh_data_bindings()

    def btn_show_more_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.mb_count_show = min(self.mb_count_show + 10, self.mb_count)
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
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(roles=['member'])
        self.refresh_data_bindings()
        self.tb_mb_search.text = None
        self.btn_clear_search.visible = False

    def btn_notactive_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(
            q.all_of(
                q.all_of(
                    paypal_sub_id=q.not_(None),
                    payment_enrolled=False,
                    roles=q.none_of(['leader'], ['screener'])
                ),
                q.all_of(
                    paypal_sub_id=q.not_(None),
                    payment_enrolled=False,
                    roles=['member']
                )
            )
        )
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True

    def btn_nosub_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.members = Global.users.search(
            q.all_of(
                q.all_of(
                    paypal_sub_id=None,
                    roles=q.none_of(['leader'], ['screener'])
                ),
                q.all_of(
                    paypal_sub_id=None,
                    roles=['member']
                )
            )
        )
        self.refresh_data_bindings()
        self.btn_clear_search.visible = True



