"""Test the form functionality."""
import unittest
import anvil.server
import anvil.users
import time

from . import Global


class Admin(unittest.TestCase):
    """Unit tests for admins."""

    def setUp(self):
        self.user = Global.user
        from .HomeForm import HomeForm
        self.form = HomeForm()
        Global.user = anvil.server.call('get_test_user', 'Admin')
        _ = anvil.users.force_login(Global.user, remember=True)
        self.user = Global.user

    def test_load_members(self):
        """Load links for admin"""
        pass

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


class TestAdmin(unittest.TestCase):
    """Tests for admins. Server tests."""

    def test_get_users(self):
        """Get users"""
        pass

    def test_get_user_notes(self):
        assert False

    def test_save_user_notes(self):
        assert False

    def test_notify_accept(self):
        assert False