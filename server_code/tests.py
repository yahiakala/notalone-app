"""Test the functions that are not callables."""
import anvil.server
import anvil.users

from .helpers import permission_required
from . import payments
from . import tasks


@permission_required('auth_dev')
def test_clean_up_user():
    user = anvil.users.get_user(allow_remembered=True)
    tasks.clean_up_user(user)


@permission_required('auth_dev')
def test_clean_up_users():
    tasks.clean_up_users()


@permission_required('auth_dev')
def test_get_paypal_auth():
    payments.get_paypal_auth()


@permission_required('auth_dev')
def test_get_subscriptions():
    user = anvil.users.get_user(allow_remembered=True)
    if user['paypal_sub_id']:
        payments.get_subscriptions(user['paypal_sub_id'])


@permission_required('auth_dev')
def test_check_subs():
    payments.check_subs()


@permission_required('auth_dev')
def test_check_sub():
    user = anvil.users.get_user(allow_remembered=True)
    payments.check_sub(user)