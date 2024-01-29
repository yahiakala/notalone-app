"""Test the form functionality."""
import unittest
import anvil.server
import anvil.users
import time

from . import Global


class Screener(unittest.TestCase):
    
    def setUp(self):
        self.user = Global.user
        from .HomeForm import HomeForm
        self.form = HomeForm()
        Global.user = anvil.server.call('get_test_user', 'Screener')
        _ = anvil.users.force_login(Global.user, remember=True)
        self.user = Global.user

    def test_load_screener(self):
        """Load links for screener"""
        assert(self.form.link_apply.visible == False)
        assert(self.form.link_profile.visible == True)
        assert(self.form.link_applicants.visible == True)
        assert(self.form.link_members.visible == False)
        self.form.link_applicants.raise_event('click')

    def test_form_visible(self):
        assert False

    def test_accept_member(self):
        assert False

    def test_confirm_member(self):
        assert False

    def test_write_notes(self):
        assert False