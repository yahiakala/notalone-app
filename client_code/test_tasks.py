"""Test tasks module."""
import unittest
import anvil.server
import time

from . import Global


class TestNewApplicant(unittest.TestCase):
    """User should have no tenant and no auth privileges."""

    def test_get_screener_link(self):
        """Get the screener URL after joining tenant"""
        user = Global.user
        tenants = anvil.server.call('get_tenants')
        if user['tenant'] is None:
            user = anvil.server.call('join_tenant', tenants.search()[0].get_id())
            screenerlink = anvil.server.call('get_screener_link')
            print(screenerlink)
            assert('calendly' in screenerlink['booking_link'])
            user = anvil.server.call('leave_tenant')

    def test_get_tenants(self):
        """Get all the tenants you can request to join."""
        user = Global.user
        tenants = anvil.server.call('get_tenants')
        if tenants:
            tenants = tenants.search()
        if user['tenant'] is None:
            assert(len(tenants) > 0)
        else:
            assert(len(tenants) == 0)

    def test_join_tenant(self):
        """Join a tenant."""
        user = Global.user
        tenants = anvil.server.call('get_tenants')
        if user['tenant'] is None:
            user = anvil.server.call('join_tenant', tenants.search()[0].get_id())
            assert(user['tenant'] is not None)
            user = anvil.server.call('leave_tenant')
            assert(user['tenant'] is None)
        else:
            pass

    def test_update_user(self):
        """Try to update a user."""
        user = Global.user
        anvil.server.call('update_user', user)
        # TODO: check changes
        
    def test_try_get_users(self):
        """Try to get users."""
        # TODO: check user privileges and change test logic based on that.
        try:
            _ = anvil.server.call('get_users')
        except anvil.server.PermissionDenied:
            pass


class TestAdmin(unittest.TestCase):
    """Tests for admins."""

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
    