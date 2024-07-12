"""Test the functions that are not callables."""
from anvil.tables import app_tables
import anvil.users


def create_test_data():
    # user who is on a volunteer-req payment tier who does not have a role.
    # Sample tenant
    pass


@anvil.server.callable(require_user=True)
def impersonate_user(email):
    if 'debug' in anvil.server.get_app_origin():
        new_user = app_tables.users.get(email=email)
        anvil.users.force_login(new_user)
        return new_user