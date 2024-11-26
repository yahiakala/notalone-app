import anvil.server
import anvil.tables.query as q
from anvil import *
from anvil_extras import routing

from ..Global import Global
from ._anvil_designer import MembersTemplate


@routing.route("/members", template="Router", url_keys=[routing.ANY])
class Members(MembersTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.members = [None, None, None]
        self.rp_members.items = self.members

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.users = Global.users

            if "role" in self.url_dict:
                self.start_search()
                self.members = anvil.server.call(
                    "search_users_by_role", Global.tenant_id, self.url_dict["role"]
                )
                self.rp_members.items = self.members
                self.pagination_1.data_grid = self.dg_members
                self.pagination_1.repeating_panel = self.rp_members
                # Show role name in label
                self.lbl_role_filter.text = (
                    f"Members with role: {self.url_dict['role']}"
                )
                self.lbl_role_filter.visible = True
                self.end_search()
            else:
                # Hide role label if no role filter
                self.lbl_role_filter.visible = False

            if self.members == [None, None, None]:
                self.members = Global.users.search(
                    q.fetch_only(
                        "user",
                        "first_name",
                        "last_name",
                        user=q.fetch_only("email", "last_login", "signed_up"),
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
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = anvil.server.call(
                "search_users_by_text", Global.tenant_id, self.tb_mb_search.text
            )
            self.end_search()

    def btn_clear_search_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = Global.users.search(
                q.fetch_only(
                    "user",
                    "first_name",
                    "last_name",
                    user=q.fetch_only("email", "last_login", "signed_up"),
                )
            )
            self.end_search()
            self.tb_mb_search.text = None
            self.btn_clear_search.enabled = False
            # Hide role label when clearing search
            self.lbl_role_filter.visible = False

    def btn_qf_admins_click(self, **event_args):
        """Get admins."""
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = anvil.server.call(
                "search_users_by_role", Global.tenant_id, "Admin"
            )
            self.end_search()

    def btn_qf_applicants_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = anvil.server.call(
                "search_users_by_role", Global.tenant_id, "Applicant"
            )
            self.end_search()

    def btn_qf_inactive_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = anvil.server.call(
                "search_users_by_role", Global.tenant_id, "Approved"
            )
            self.end_search()

    def btn_qf_disabled_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = anvil.server.call(
                "search_users_by_role", Global.tenant_id, None
            )
            self.end_search()

    def btn_qf_regular_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.start_search()
        with anvil.server.no_loading_indicator:
            self.members = anvil.server.call(
                "search_users_by_role", Global.tenant_id, "Member"
            )
            self.end_search()

    def reset_buttons(self, **event_args):
        self.btn_qf_admins.role = "tonal-button"
        self.btn_qf_applicants.role = "tonal-button"
        self.btn_qf_disabled.role = "tonal-button"
        self.btn_qf_inactive.role = "tonal-button"
        self.btn_qf_regular.role = "tonal-button"

    def start_search(self):
        self.reset_buttons()
        self.btn_clear_search.text = "Searching..."
        self.btn_clear_search.italic = True
        self.btn_clear_search.enabled = True
        self.rp_members.items = [None, None, None]

    def end_search(self):
        self.rp_members.items = self.members
        self.pagination_1.repeating_panel = self.rp_members
        self.btn_clear_search.text = "Clear Search"
        self.btn_clear_search.italic = False
