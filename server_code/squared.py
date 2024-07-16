import anvil.server
import anvil.users
import anvil.email

from anvil_squared import auth


@anvil.server.callable
def login_with_email_custom(email, password):
    """Try to log user in without MFA. Return exception if user has MFA configured."""
    return auth.login_with_email_squared(email, password)


@anvil.server.callable
def signup_with_email_custom(email, password, app_name):
    """Signup a new user. Require them to confirm email before logging in."""
    return auth.signup_with_email_squared(email, password, app_name)


@anvil.server.callable(require_user=True)
def add_mfa_method(password, mfa_method):
    """Add an mfa method."""
    return auth.add_mfa_method_squared(password, mfa_method)


@anvil.server.callable(require_user=True)
def delete_mfa_method(password, id):
    """Delete mfa method if the password is correct."""
    return auth.delete_mfa_method_squared(password, id)