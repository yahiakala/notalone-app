"""Test the functions that are not callables."""
import anvil.server
import anvil.users
from anvil.tables import app_tables

from . import payments
from . import tasks

from anvil_extras import authorisation
from anvil_extras.authorisation import authorisation_required

authorisation.set_config(get_roles='usermap')


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def impersonate_user(email):
    new_user = app_tables.users.get(email=email)
    anvil.users.force_login(new_user)
    return new_user


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def test_clean_up_user():
    user = anvil.users.get_user(allow_remembered=True)
    tasks.clean_up_user(user)


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def test_clean_up_users():
    tasks.clean_up_users()


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def test_get_paypal_auth():
    payments.get_paypal_auth()


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def test_get_subscriptions():
    user = anvil.users.get_user(allow_remembered=True)
    if user['paypal_sub_id']:
        payments.get_subscriptions(user['paypal_sub_id'])


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def test_check_subs():
    appuser = app_tables.users.get(last_name='Applicant')
    appuser['paypal_sub_id'] = 'alsdjfwlf'
    # TODO: add a blank paypal_sub_id for a different user
    payments.check_subs()


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def test_check_sub():
    user = anvil.users.get_user(allow_remembered=True)
    payments.check_sub(user)


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def reassign_roles_dev(user_dict, role_dict):
    return tasks.reassign_roles(user_dict, role_dict)


@anvil.server.callable(require_user=True)
@authorisation_required('dev')
def get_test_user(user_name):
    """Get a test user."""
    return app_tables.users.get(last_name=user_name, auth_dev=True)


def create_test_data():
    # user who is on a volunteer-req payment tier who does not have a role.
    # Sample tenant
    pass