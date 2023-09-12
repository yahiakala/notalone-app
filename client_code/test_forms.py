"""Test the form functionality."""
import unittest
import anvil.server
import time

from . import Global


class TestLoadForms(unittest.TestCase):
    """Load all Forms."""

    def test_load_applicant_0(self):
        """Try and fail to load other links."""
        user = Global.user
        # TODO: fail to load other links

    def test_load_applicant_1(self):
        """Load links for user with auth_booking."""
        user = Global.user
        from .HomeForm import HomeForm
        form = HomeForm()
        if user['auth_booking']:
            form.link_apply.raise_event('click')
        # TODO: fail to load other links

    def test_load_applicant_2(self):
        """Load links for applicant in second stage."""
        user = Global.user
        from .HomeForm import HomeForm
        form = HomeForm()
        form.link_profile.raise_event('click')
        # TODO: fail to load other links

    def test_load_screener(self):
        """Load links for screener"""
        user = Global.user
        from .HomeForm import HomeForm
        form = HomeForm()
        form.link_applicants.raise_event('click')
        # TODO: fail to load other links

    def test_load_members(self):
        """Load links for admin"""
        user = Global.user
        from .HomeForm import HomeForm
        form = HomeForm()
        form.link_members.raise_event('click')
        # TODO: fail to load other links