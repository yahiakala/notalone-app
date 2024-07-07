from ._anvil_designer import MembersTemplate
from anvil import *
import anvil.tables.query as q
import anvil.server

from ..Global import Global
from anvil_extras import routing
# import datetime as dt
# from anvil_extras.logging import TimerLogger
# from anvil_squared.utils import print_timestamp


@routing.route('/members', template='Router')
class Members(MembersTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.members = [None, None, None]
        self.rp_members.items = self.members

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
                self.rp_members.items = self.members

            self.pagination_1.data_grid = self.dg_members
            self.pagination_1.repeating_panel = self.rp_members

    def tb_mb_search_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.btn_clear_search.text = 'Searching...'
        self.btn_clear_search.italic = True
        self.btn_clear_search.enabled = True
        self.rp_members.items = [None, None, None]
        with anvil.server.no_loading_indicator:
            self.user_search = anvil.server.call('search_users', Global.tenant_id, self.tb_mb_search.text)

            self.members = Global.users.search(
                q.fetch_only(
                    'user',
                    user=q.fetch_only(
                        'email', 'first_name', 'last_name', 'last_login', 'signed_up'
                    )
                ),
                q.any_of(
                    user=q.any_of(*self.user_search),
                    notes=q.ilike('%' + self.tb_mb_search.text + '%')
                )
            )
            self.rp_members.items = self.members
            self.pagination_1.repeating_panel = self.rp_members
            self.btn_clear_search.text = 'Clear Search'
            self.btn_clear_search.italic = False

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.rp_members.items = [None, None, None]
        self.btn_qf_admins.role = 'tonal-button'
        self.btn_qf_applicants.role = 'tonal-button'
        self.btn_qf_disabled.role = 'tonal-button'
        self.btn_qf_inactive.role = 'tonal-button'
        self.btn_qf_regular.role = 'tonal-button'
        self.form_show()
        self.tb_mb_search.text = None
        self.btn_clear_search.enabled = False

    def btn_qf_admins_click(self, **event_args):
        """Get admins."""
        # ['see_members']
        pass

    def btn_qf_applicants_click(self, **event_args):
        """This method is called when the button is clicked"""
        # TODO: apply filters
        # ['book_interview']

    def btn_qf_inactive_click(self, **event_args):
        """This method is called when the button is clicked"""
        # not see_profile, not book_interview
        pass

    
    def btn_qf_disabled_click(self, **event_args):
        """This method is called when the button is clicked"""
        # has see_profile, does not have see_forum
        pass

    def apply_filters(self, **event_args):
        pass
        # enable to check if ONLY one role or ONLY certain permissions

    def reset_buttons(self, **event_args):
        self.btn_qf_admins.role = 'tonal-button'
        self.btn_qf_applicants.role = 'tonal-button'
        self.btn_qf_disabled.role = 'tonal-button'
        self.btn_qf_inactive.role = 'tonal-button'
        self.btn_qf_regular.role = 'tonal-button'
        self.quick_filters = ''


