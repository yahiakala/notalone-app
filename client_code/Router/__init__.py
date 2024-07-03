from ._anvil_designer import RouterTemplate
from anvil import *
import anvil.users

# from ..HomeAnonComponent import HomeAnonComponent
from ..Home import Home
from ..BookingComponent import BookingComponent
# from ..ProfileComponent import ProfileComponent
from ..MemberDetail import MemberDetail
from ..ApplicantsComponent import ApplicantsComponent
from ..MembersComponent import MembersComponent
from ..FinComponent import FinComponent
from ..VolunteerComponent import VolunteerComponent
from ..LoadingPopup import LoadingPopup

from anvil_extras.logging import TimerLogger
from anvil_extras import routing
from ..Global import Global
from anvil_squared.utils import print_timestamp


@routing.template(path='app', priority=1, condition=lambda: Global.get_s('tenant_id') is not None)
class Router(RouterTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)

        self.link_home.tag.url_hash = 'app/home'
        self.link_apply.tag.url_hash = 'app/apply'
        self.link_profile.tag.url_hash = 'app/profile'
        self.link_applicants.tag.url_hash = 'app/applicants'
        self.link_members.tag.url_hash = 'app/members'
        self.link_fin.tag.url_hash = 'app/financials'
        self.link_volunteers.tag.url_hash = 'app/volunteers'

        self.link_home.tag.globals = []
        self.link_apply.tag.globals = []
        self.link_profile.tag.globals = []
        self.link_members.tag.globals = ['users']
        self.link_fin.tag.globals = []
        self.link_volunteers.tag.globals = []
        
        self.btn_test.tag.url_hash = 'app/tests'
        self.load_globals = []

    def populate_globals(self):
        with anvil.server.no_loading_indicator:
            self.user = Global.user
            self.set_account_state(self.user)
            Global.task_tenanted = anvil.server.call('get_tenanted_data_call_bk', Global.tenant_id)
    
            if Global.is_mobile:
                self.lbl_app_title.visible = False
                self.link_forum_nav.text = ''
        
        print_timestamp('Populated globals on Router')

    def link_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.users.logout()
        self.set_account_state(None)
        routing.clear_cache()
        Global.user = None  # Haven't tested this.
        routing.set_url_hash('', load_from_cache=False)

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
        alert('For help, contact ' + Global.tenant_info['email'])

    def tb_impersonate_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.user = anvil.server.call('impersonate_user', self.tb_impersonate.text)
        # reset the globals
        Global.clear_global_attributes()
        Global.user = self.user
        self.refresh_everything()
        self.nav_click(self.link_home)

    def check_if_loaded(self, keys):
        for key in keys:
            if Global.get_s(key) is None:
                return False
        return True
    
    def nav_click(self, sender, **event_args):
        if not self.check_if_loaded(sender.tag.globals):
            self.img_loading.visible = True
            self.load_globals = sender.tag.globals
            self.ti_globals.interval = 1

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

    def ti_load_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        self.ti_load.interval = 0
        self.populate_globals()

    def ti_globals_tick(self, **event_args):
        """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
        if self.check_if_loaded(self.load_globals):
            self.ti_globals.interval = 0
            self.img_loading.visible = False
