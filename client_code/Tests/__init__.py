from ._anvil_designer import TestsTemplate
from anvil import *
from anvil_extras import routing
from ..Global import Global


@routing.route('/tests', template='Router')
class Tests(TestsTemplate):
    def __init__(self, **properties):
        """
        Selectively load test modules depending on who is logged in.
        There should be users in the users table with the following last names:
        Applicant 0: An applicant to the community without 'auth_profile'
        Member: A member in the community with 'auth_profile'
        Screener: A screener/interviewer with privilege 'auth_screenings'
        Admin: An administrator with the privilege 'auth_members'
        """
        # Set Form properties and Data Bindings.
        self.user = Global.user
        self.test_mods = []
        if self.user['last_name'] == 'Applicant 0':
            from .. import test_applicant
            test_mods = [test_applicant]
        elif self.user['last_name'] == 'Member':
            from .. import test_member
            test_mods = [test_member]
        elif self.user['last_name'] == 'Screener':
            from .. import test_screener
            test_mods = [test_screener]
        elif self.user['last_name'] == 'Admin':
            from .. import test_admin, test_server
            test_mods = [test_admin, test_server]
        self.init_components(**properties)
        self.ctests.test_modules = test_mods
        self.ctests.card_roles=['tonal-card', 'elevated-card', 'elevated-card']
        self.ctests.icon_size=30
        self.ctests.btn_role='filled-button'
