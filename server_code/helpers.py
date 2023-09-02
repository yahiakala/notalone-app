import anvil.server
from anvil.tables import app_tables
import anvil.tables.query as q

from functools import wraps, partial


def permission_required(permissions):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return anvil.server.callable(require_user=partial(check_user_auth, permissions=permissions))(wrapper)
    return decorator


def check_user_auth(user, permissions):
    print('Checking user auth')
    if user is None:
        return False
        
    if isinstance(permissions, str):
        required_permissions = set([permissions])
    else:
        required_permissions = set(permissions)

    try:
        user_permissions = set(
            [
                permission
                for permission in required_permissions
                if user[permission] == True
            ]
        )
    except Exception:
        return False
        
    if not required_permissions.issubset(user_permissions):
        return False
        
    return True