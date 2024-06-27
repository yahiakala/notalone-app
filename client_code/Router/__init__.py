from ._anvil_designer import RouterTemplate
from anvil import *
import anvil.users

# from ..HomeAnonComponent import HomeAnonComponent
from ..Home import Home
from ..BookingComponent import BookingComponent
from ..ProfileComponent import ProfileComponent
from ..ApplicantsComponent import ApplicantsComponent
from ..MembersComponent import MembersComponent
from ..FinComponent import FinComponent
from ..VolunteerComponent import VolunteerComponent

from anvil_extras import routing
from ..Global import Global
from anvil_squared.utils import print_timestamp
import time


# lambda: Global.get_no_call('tenant_id') is not None
@routing.template(path='app', priority=1, condition=lambda: Global.get_no_call('tenant_id') is not None)
class Router(RouterTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        self.link_home.tag.url_hash = 'app/home'
        self.link_home.tag.globals = ['user']
        self.link_apply.tag.url_hash = 'app/apply'
        self.link_profile.tag.url_hash = 'app/profile'
        self.link_applicants.tag.url_hash = 'app/applicants'
        self.link_members.tag.url_hash = 'app/members'
        self.link_fin.tag.url_hash = 'app/financials'
        self.link_volunteers.tag.url_hash = 'app/volunteers'
        self.btn_test.tag.url_hash = 'app/tests'

        self.user = Global.user
        self.set_account_state(self.user)
        
        if Global.get_no_call('user_data') is None:
            print_timestamp('Starting timer')
            self.task = anvil.server.call('get_user_data', Global.tenant_id)
            self.timer_user_data.interval = 2

        # self.nav_click(self.link_home)

        if Global.is_mobile:
            self.lbl_app_title.visible = False
            self.link_forum_nav.text = ''


    def link_login_click(self, **event_args):
        """This method is called when the link is clicked"""
        Global.user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=True)
        self.set_account_state(Global.user)
        self.refresh_data_bindings()
        self.nav_click(self.link_home)

    def link_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.users.logout()
        self.set_account_state(None)
        Global.user = None  # Haven't tested this.
        routing.set_url_hash('', load_from_cache=False)

    def set_account_state(self, user):
        print_timestamp('set_account_state')
        self.link_logout.visible = user is not None
        self.link_login.visible = user is None
        
        self.link_apply.visible = False
        self.link_profile.visible = False
        self.link_applicants.visible = False
        self.link_members.visible = False
        self.link_fin.visible = False
        self.link_volunteers.visible = False
        self.link_forum_nav.visible = False
        self.lbl_user.visible = False
        self.link_help.visible = False
        self.btn_test.visible = False
        self.tb_impersonate.visible = False

        self.permissions = Global.permissions
        
        if user:
            self.lbl_user.visible = True
            self.lbl_user.text = user['email']
            self.link_apply.visible = 'book_interview' in self.permissions
            self.link_profile.visible = 'see_profile' in self.permissions
            self.link_applicants.visible = 'see_applicants' in self.permissions
            self.link_members.visible = 'see_members' in self.permissions
            self.link_fin.visible = 'see_financials' in self.permissions
            self.link_volunteers.visible = 'see_members' in self.permissions  # TODO
            self.link_forum_nav.visible = (
                'see_forum' in self.permissions and
                user['first_name'] != '' and
                user['last_name'] != ''
            )
            if 'dev' in self.permissions:
                self.btn_test.visible = True
                self.tb_impersonate.visible = True
                from ..Tests import Tests

            self.lbl_app_title.text = [i for i in Global.my_tenants if i['tenant_id'] == Global.tenant_id][0]['name']
            self.link_help.visible = True

    def refresh_everything(self, **event_args):
        """Refresh mainly the menu links."""
        self.user = Global.user
        self.set_account_state(self.user)
        self.refresh_data_bindings()

    def link_forum_nav_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.js.window.location.href = Global.forumlink

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        if self.user and self.user['tenant']:
            alert('For help, contact ' + self.user['tenant']['email'])

    def tb_impersonate_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.user = anvil.server.call('impersonate_user', self.tb_impersonate.text)
        # reset the globals
        Global.clear_global_attributes()
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

    def timer_user_data_tick(self, **event_args):
        """Use a timer to load all the globals."""
        print_timestamp('timer_user_data_tick')
        with anvil.server.no_loading_indicator:
            if self.task.is_completed():
                print_timestamp('task_done')
                user_data = self.task.get_return_value()
                Global.user_data = user_data
                self.timer_user_data.interval = 0
                for key, val in user_data.items():
                    if Global.get_no_call(key) is None:
                        print_timestamp(f"task_done: setting value for {key}")
                        setattr(Global, key, val)
            else:
                # Populate some globals based on task state.
                states = self.task.get_state()
                print_timestamp('Checking states')
                print(states)
                for key, val in states.items():
                    if Global.get_no_call(key) is None:
                        print_timestamp(f"task_state: setting value for {key}")
                        setattr(Global, key, val)
                    
                