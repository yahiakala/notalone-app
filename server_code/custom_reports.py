import anvil.server
from anvil.tables import app_tables
from .helpers import validate_user, usermap_row_to_dict


@anvil.server.callable(require_user=True)
def no_volunteer(tenant_id, tenant=None):
    """look for people who ONLY have the 'Member' role and fee=10."""
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if 'see_members' in permissions:
        return None

    member_role = app_tables.roles.get(tenant=tenant, name='Member')
    usermaps = app_tables.usermap.search(roles=[member_role], fee=10)
    user_list = []
    for usermap in usermaps:
        if len(usermap['roles']) == 1:
            user_list.append(usermap_row_to_dict(usermap))
    return user_list
