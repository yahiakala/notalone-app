"""Test the functions that are not callables."""
import anvil.server
import anvil.users

from .helpers import permission_required
from . import payments
from . import tasks


@permission_required('auth_dev')
def test_clean_up_user():
    user = anvil.users.get_user(allow_remembered=True)
    clean_up_user(user)

@permission_required('auth_dev')
def test_clean_up_users():
    clean_up_users()

@permission_required('auth_dev')
def test_get_paypal_auth():
    payments.get_paypal_auth()


@permission_required('auth_dev')
def test_get_subscriptions():
    payments.get_subscriptions()