"""Test the form functionality."""
import unittest
import anvil.server
import anvil.users
import time

from . import Global


class TestLoadForms(unittest.TestCase):
    """Load all Forms."""

    def setUp(self):
        self.user = Global.user
        from .HomeForm import HomeForm
        self.form = HomeForm()
        self.user = anvil.server.call('')
        self.user = anvil.users.force_login(self.user, remember=True)

    def test_load_applicant_0(self):
        """Try and fail to load other links."""
        if self.user['last_name'] == 'Applicant':
            assert(self.form.link_apply.visible == False)
            assert(self.form.link_members.visible == False)
            assert(self.form.link_profile.visible == False)
            assert(self.form.link_applicants.visible == False)
            self.form.link_home.raise_event('click')

    def test_load_applicant_1(self):
        """Load links for user with auth_booking."""
        if self.user['last_name'] == 'Applicant 1':
            assert(self.form.link_apply.visible == True)
            assert(self.form.link_members.visible == False)
            assert(self.form.link_profile.visible == False)
            assert(self.form.link_applicants.visible == False)
            self.form.link_apply.raise_event('click')

    def test_load_applicant_2(self):
        """Load links for applicant in second stage."""
        if self.user['last_name'] == 'Applicant 2':
            assert(self.form.link_apply.visible == False)
            assert(self.form.link_profile.visible == True)
            assert(self.form.link_applicants.visible == False)
            assert(self.form.link_members.visible == False)
            self.form.link_profile.raise_event('click')

    def test_load_screener(self):
        """Load links for screener"""
        if self.user['last_name'] == 'Screener':
            assert(self.form.link_apply.visible == False)
            assert(self.form.link_profile.visible == True)
            assert(self.form.link_applicants.visible == True)
            assert(self.form.link_members.visible == False)
            self.form.link_applicants.raise_event('click')

    def test_load_members(self):
        """Load links for admin"""
        if self.user['last_name'] == 'Admin':
            assert(self.form.link_apply.visible == False)
            assert(self.form.link_profile.visible == True)
            assert(self.form.link_applicants.visible == True)
            assert(self.form.link_members.visible == True)
            self.form.link_members.raise_event('click')


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
        if self.user['last_name'] == 'Applicant':
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


class ProfileForm(unittest.TestCase):
    """Test the profile form."""
    
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
        else:
            assert(self.home.link_profile.visible == True)

    def test_profile_pay(self):
        """Make sure the home screen is the current form after payment button clicked."""
        pass

    def test_profile_info(self):
        """Validate profile info."""
        pass

    def test_profile_plan(self):
        """Select plan."""
        pass


class ApplicantForm(unittest.TestCase):
    """Test the screener form."""

    def test_form_visible(self):
        assert False

    def test_accept_member(self):
        assert False

    def test_confirm_member(self):
        assert False

    def test_write_notes(self):
        assert False


class MemberForm(unittest.TestCase):
    """Test the Member form."""

    def test_members_visible(self):
        if self.user['last_name'] == 'Admin':
            assert(self.home.link_members.visible == True)

    def test_member_search(self):
        """Search for a member."""
        assert False

    def test_member_remove_restore(self):
        """Remove and restore a member."""
        assert False

    def test_member_quick_filters(self):
        """Apply quick filters."""
        assert False

    def test_member_permissions(self):
        """Reassign permissions."""
        assert False

    def test_member_refresh(self):
        """Refresh member status."""
        assert False

    def test_member_notes(self):
        """Get member notes."""
        assert False