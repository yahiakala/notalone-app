"""Server tests."""
import unittest
import anvil.server
import time


class ServerFuncs(unittest.TestCase):
    """Test various server functions."""

    def test_check_subs(self):
        """Various server funcs."""
        anvil.server.call('test_clean_up_user')
        anvil.server.call('test_clean_up_users')
        anvil.server.call('test_get_paypal_auth')
        anvil.server.call('test_get_subscriptions')
        anvil.server.call('test_check_subs')
        anvil.server.call('test_check_sub')