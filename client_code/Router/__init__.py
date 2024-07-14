from ._anvil_designer import RouterTemplate
from anvil import *
import anvil.users
import anvil.server

from ..Home import Home
from ..BookingComponent import BookingComponent
from ..Setup import Setup
from ..MemberDetail import MemberDetail
from ..Members import Members
from ..FinComponent import FinComponent
from ..VolunteerComponent import VolunteerComponent
from ..LoadingPopup import LoadingPopup
from ..PaymentConfirm import PaymentConfirm

from anvil_extras.logging import TimerLogger
from anvil_extras import routing
from ..Global import Global
from anvil_squared.utils import print_timestamp


@routing.template(path='app', priority=5, condition=lambda: Global.get_s('tenant') is not None)
class Router(RouterTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        self.link_home.tag.url_hash = 'app/home'
        self.link_apply.tag.url_hash = 'app/apply'
        self.link_profile.tag.url_hash = 'app/profile'
        self.link_members.tag.url_hash = 'app/members'
        self.link_fin.tag.url_hash = 'app/financials'
        self.link_volunteers.tag.url_hash = 'app/volunteers'
        self.link_admin.tag.url_hash = 'app/admin'
        
        self.populate_globals()

    def populate_globals(self):
        self.user = Global.user
        self.set_account_state(self.user)

        if Global.is_mobile:
            self.lbl_app_title.visible = False
            self.link_forum_nav.text = ''
        
        print_timestamp('Populated globals on Router')

    def link_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        with anvil.server.no_loading_indicator:
            anvil.users.logout()
            self.set_account_state(None)
            routing.clear_cache()
            Global.clear_global_attributes()
            routing.set_url_hash('sign', load_from_cache=False)

    def set_account_state(self, user):
        print_timestamp('set_account_state')
        self.link_logout.visible = user is not None

        self.permissions = Global.permissions
        print(self.permissions)
        
        if user:
            self.lbl_user.text = user['email']
            self.lbl_user.role = None
            self.link_apply.visible = 'book_interview' in self.permissions
            self.link_profile.visible = 'see_profile' in self.permissions
            self.link_members.visible = 'see_members' in self.permissions
            self.link_fin.visible = 'see_financials' in self.permissions
            self.link_volunteers.visible = 'see_members' in self.permissions  # TODO
            self.link_admin.visible = 'delete_admin' in self.permissions
            if 'debug' in anvil.server.get_app_origin():
                # TODO: change to app origin check debug
                self.tb_impersonate.visible = True

            self.lbl_app_title.text = Global.tenant['name']
            self.link_help.visible = True

    def refresh_everything(self, **event_args):
        """Refresh mainly the menu links."""
        self.user = Global.user
        self.set_account_state(self.user)
        self.refresh_data_bindings()

    def link_forum_nav_click(self, **event_args):
        """This method is called when the link is clicked"""
        if 'see_forum' not in self.permissions:
            routing.alert('Please make sure your membership is in good standing before accessing the forum.')
        else:
            anvil.js.window.location.href = Global.tenant['discourse_url']

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        alert('For help, contact ' + Global.tenant['email'])

    def tb_impersonate_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.user = anvil.server.call('impersonate_user', self.tb_impersonate.text)
        # reset the globals
        Global.clear_global_attributes()
        routing.clear_cache()
        Global.user = self.user
        self.refresh_everything()
        self.nav_click(self.link_home)
    
    def nav_click(self, sender, **event_args):
        if sender.tag.url_hash == '':
            if Global.user:
                self.set_account_state(Global.user)
                routing.set_url_hash('app')
            else:
                routing.set_url_hash('')
        else:
            routing.set_url_hash(sender.tag.url_hash)

    def on_navigation(self, url_hash, url_pattern, url_dict, unload_form):
        for link in self.cp_sidebar.get_components():
            if type(link) == Link:
                link.role = 'selected' if link.tag.url_hash == url_hash else None
        if url_hash in ['homeanon', 'homedetail', 'app']:
            self.link_home.role = 'selected'
            
    def on_form_load(self, url_hash, url_pattern, url_dict, form):
        """Any time a form is loaded."""
        self.on_navigation(url_hash, url_pattern, url_dict, form)