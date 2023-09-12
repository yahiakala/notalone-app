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
        from .BookingComponent import BookingComponent
        self.form = BookingComponent()
        print('')

    def test_apply_now_visible(self):
        if self.user['auth_booking']:
            assert(self.form.link_apply.visible == True)
        else:
            assert(self.form.link_apply.visible == False)