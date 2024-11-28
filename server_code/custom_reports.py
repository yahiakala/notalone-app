import anvil.server
from anvil.tables import app_tables
from anvil_squared.helpers import print_timestamp

from .helpers import list_to_csv, usermap_row_to_dict, validate_user


@anvil.server.callable(require_user=True)
def custom_0001(tenant_id, tenant=None, verbose=True):
    """look for people who ONLY have the 'Member' role and fee=10."""
    print_timestamp("custom_0001")
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if "see_members" not in permissions:
        print_timestamp("authorisation required.")
        return None

    member_role = app_tables.roles.get(tenant=tenant, name="Member")
    usermaps = app_tables.usermap.search(roles=[member_role], fee=10)
    if verbose:
        print_timestamp("usermaps")
        print(usermaps)
        print(len(usermaps))
    user_list = []
    for usermap in usermaps:
        if len(usermap["roles"]) == 1:
            try:
                user_list.append(usermap_row_to_dict(usermap))
            except anvil.tables.RowDeleted:
                # usermap.delete()
                pass
    if verbose:
        print_timestamp("user_list")
        print(user_list)

    if len(user_list) == 0:
        print_timestamp("Empty Report")
        return None

    return list_to_csv(user_list)
