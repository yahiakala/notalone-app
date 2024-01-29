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
        assert(self.form.link_apply.visible == False)
        assert(self.form.link_profile.visible == True)
        assert(self.form.link_applicants.visible == True)
        assert(self.form.link_members.visible == True)
        self.form.link_members.raise_event('click')

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
        user = Global.user
        if user['auth_members']:
            users = Global.users.search()
            assert(len(users) > 0)

    def test_get_applicants(self):
        """Get applicants"""
        user = Global.user
        if user['auth_screenings']:
            apps = Global.applicants

    def test_reassign_roles(self):
        """Reassign a role"""
        user = Global.user
        if user['auth_members']:
            users = Global.users.search()
            role_dict = {'auth_forumchat': False}
            user = anvil.server.call('reassign_roles', users[0], role_dict)
            assert(user['auth_forumchat'] == False)
            role_dict = {'auth_forumchat': True}
            user = anvil.server.call('reassign_roles', users[0], role_dict)
            assert(user['auth_forumchat'] == True)

    def test_get_user_notes(self):
        assert False

    def test_save_user_notes(self):
        assert False

    def test_notify_accept(self):
        assert False