"""Test the form functionality."""
import unittest
import anvil.server
import time

from . import Global


class TestLoadForms(unittest.TestCase):
    """Load all Forms."""

    def setUp(self):
        self.user = Global.user
        from .HomeForm import HomeForm
        self.form = HomeForm()

    def test_load_applicant_0(self):
        """Try and fail to load other links."""
        pass
        # TODO: fail to load other links

    def test_load_applicant_1(self):
        """Load links for user with auth_booking."""
        if self.user['auth_booking']:
            self.form.link_apply.raise_event('click')
        # TODO: fail to load other links

    def test_load_applicant_2(self):
        """Load links for applicant in second stage."""
        self.form.link_profile.raise_event('click')
        # TODO: fail to load other links

    def test_load_screener(self):
        """Load links for screener"""
        self.form.link_applicants.raise_event('click')
        # TODO: fail to load other links

    def test_load_members(self):
        """Load links for admin"""
        self.form.link_members.raise_event('click')
        # TODO: fail to load other links


class ApplyNowForm(unittest.TestCase):
    """Apply now form functionality."""

    def setUp(self):
        self.user = Global.user
        # from .BookingComponent import BookingComponent
        from .HomeForm import HomeForm
        # self.form = BookingComponent()
        self.home = HomeForm()
        print('Setup Complete')

        if self.user['last_name'] == 'Applicant':
            Global.user = anvil.server.call('leave_tenant')
            self.user = Global.user

    def test_apply_now_visible_1(self):
        if not self.user['last_name'] == 'Applicant':
            assert(self.home.link_apply.visible == True)
        else:
            assert(self.home.link_apply.visible == False)

    def test_apply_now_visible_2(self):
        """Test that the apply now button becomes visible once you select a group."""
        if self.user['last_name'] == 'Applicant':
            assert(self.home.link_apply.visible == False)
            tenants = anvil.server.call('get_tenants')
            search_term = self.home.cmpt.tb_search_group.text = 'e'
            self.home.cmpt.tb_search_group.raise_event('pressed_enter')
            first_thing = self.home.cmpt.rp_groups.get_components()[0]
            first_thing.btn_join.raise_event('click')
            assert(self.home.link_apply.visible == True)
            Global.user = anvil.server.call('leave_tenant')
            self.user = Global.user

    def test_profile_visible(self):
        """Fill out profile after passing screening."""
        if self.user['last_name'] == 'Applicant':
            assert(self.home.link_profile.visible == False)
            tenants = anvil.server.call('get_tenants')
            search_term = self.home.cmpt.tb_search_group.text = 'e'
            self.home.cmpt.tb_search_group.raise_event('pressed_enter')
            first_thing = self.home.cmpt.rp_groups.get_components()[0]
            first_thing.btn_join.raise_event('click')

            # Now they pass screening
            Global.user = anvil.server.call('reassign_roles_dev', self.user, {'auth_profile': True})
            self.user = Global.user
            
            self.home.cmpt.raise_event('x-refresh')
            # Now they should see the profile page
            assert(self.home.link_profile.visible == True)
            
            self.user = anvil.server.call('leave_tenant')
            