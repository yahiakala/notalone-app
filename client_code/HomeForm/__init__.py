from ._anvil_designer import HomeFormTemplate
from anvil import *
import anvil.users

from functools import partial

from ..HomeAnonComponent import HomeAnonComponent
from ..HomeDetailComponent import HomeDetailComponent
from ..ApplicantComponent import ApplicantComponent
from ..ProfileComponent import ProfileComponent
from .. import Global


class HomeForm(HomeFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.link_home.add_event_handler('click', self.go_home)
        self.link_apply.add_event_handler('click', partial(self.go_page, 'apply'))
        self.link_profile.add_event_handler('click', partial(self.go_page, 'profile'))
        self.go_home()

    def link_login_click(self, **event_args):
        """This method is called when the link is clicked"""
        user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=True)
        self.set_account_state(user)
        self.go_home()

    def link_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.users.logout()
        self.set_account_state(None)
        Global.user = None  # Haven't tested this.
        self.go_home()

    def go_home(self,  **event_args):
        """This method is called when the link is clicked"""
        self.set_active_nav('home')
        if Global.user:
            self.set_account_state(Global.user)
            self.load_component(HomeDetailComponent())
        else:
            self.load_component(HomeAnonComponent())

    def require_account(self):
        user = Global.user
        if user:
            return user
        user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=True)
        self.set_account_state(user)
        return user

    def set_account_state(self, user):
        self.link_logout.visible = user is not None  # TODO: remove link
        self.link_login.visible = user is None
        self.link_apply.visible = user['roles'] is None or len(user['roles']) == 0

    def load_component(self, cmpt):
        self.content_panel.clear()
        self.content_panel.add_component(cmpt)

    def set_active_nav(self, state):
        self.link_home.role = 'selected' if state == 'home' else None
        self.link_apply.role = 'selected' if state == 'apply' else None
        self.link_profile.role = 'selected' if state == 'profile' else None

    def go_page(self, page_name, **event_args):
        """Go to a page."""
        self.set_active_nav(page_name)
        user = self.require_account()
        if page_name == 'apply' and user:
            self.load_component(ApplicantComponent())
        elif page_name == 'profile' and user:
            self.load_component(ProfileComponent())