import anvil.server
import anvil.tables.query as q
import anvil.users
from anvil.tables import app_tables
from anvil_squared.helpers import print_timestamp

from .helpers import (
    decrypt,
    get_permissions,
    get_user_roles,
    get_usermap,
    populate_roles,
    usermap_row_to_dict,
    validate_user,
    verify_tenant,
)


# --------------------
# Non tenanted globals
# --------------------
@anvil.server.callable(require_user=True)
def get_data(key):
    print_timestamp(f"get_data: {key}")
    # user = anvil.users.get_user(allow_remembered=True)
    if key == "all_permissions":
        return get_all_permissions()


@anvil.server.callable()
def get_tenant_single(user=None, tenant=None):
    """Get the tenant in this instance."""
    user = anvil.users.get_user(allow_remembered=True)
    tenant = tenant or app_tables.tenants.get()

    if not tenant:
        return None

    tenant_dict = {
        "id": tenant.get_id(),
        "name": tenant["name"],
        "email": tenant["email"],
        "discord_invite": tenant["discord_invite"],
        "discourse_url": tenant["discourse_url"],
        "waiver": tenant["waiver"],
        "logo": tenant["logo"],
        "paypal_plans": tenant["paypal_plans"],
        "custom_reports": tenant["custom_reports"],
        "donate_url": tenant["donate_url"],
    }
    if user:
        # usermap = get_usermap(tenant.get_id(), user, tenant)
        # permissions = get_permissions(tenant.get_id(), user, tenant, usermap)
        tenant, usermap, permissions = validate_user(
            tenant.get_id(), user, tenant=tenant
        )
        if "delete_members" in permissions:
            # TODO: do not return client writable
            return app_tables.tenants.client_writable().get()

    return tenant_dict


def get_all_permissions():
    return [i["name"] for i in app_tables.permissions.search()]


# ----------------
# Tenanted globals
# ----------------
@anvil.server.callable(require_user=True)
def get_tenanted_data(tenant_id, key):
    print_timestamp(f"get_tenanted_data: {key}")
    user = anvil.users.get_user(allow_remembered=True)
    # todo: verify tenant here?

    if key == "users":
        return get_users_iterable(tenant_id, user)
    elif key == "permissions":
        return get_permissions(tenant_id, user)
    elif key == "screenerlink":
        return get_screenerlink(tenant_id, user)
    # elif key == 'forumlink':
    # return get_discordlink(tenant_id, user)
    # elif key == 'discordlink':
    # return get_forumlink(tenant_id, user)
    elif key == "roles":
        return get_roles(tenant_id, user)
    elif key == "usermap":
        return get_my_usermap(tenant_id, user)
    elif key == "tenant_secrets":
        return get_tenant_secrets(tenant_id, user)


def get_my_usermap(tenant_id, user):
    tenant, usermap, permissions = validate_user(tenant_id, user)
    usermap_dict = usermap_row_to_dict(usermap)
    if "see_members" not in permissions:
        usermap_dict["notes"] = ""
    return usermap_dict


def get_tenant_secrets(tenant_id, user):
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if "delete_members" not in permissions:
        return {}

    secrets = {
        "discourse_api_key": decrypt(tenant["discourse_api_key"]),
        "discourse_secret": decrypt(tenant["discourse_secret"]),
        "paypal_client_id": decrypt(tenant["paypal_client_id"]),
        "paypal_secret": decrypt(tenant["paypal_secret"]),
        "paypal_webhook_id": decrypt(tenant["paypal_webhook_id"]),
    }
    return secrets


def get_users_iterable(tenant_id, user):
    """Get an iterable of the users."""
    tenant, usermap, permissions = validate_user(tenant_id, user)
    if "see_members" not in permissions:
        return []
    return app_tables.usermap.client_readable(
        q.only_cols("user", "first_name", "last_name", "notes"), tenant=tenant
    )


def get_screenerlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
    """Get a random interviewer name and link."""
    import random

    tenant, usermap, permissions = validate_user(
        tenant_id, user, usermap, permissions, tenant
    )
    if "book_interview" not in permissions:
        return ""

    interview_role = app_tables.roles.get(tenant=tenant, name="Interviewer")

    screeners = app_tables.usermap.search(
        booking_link=q.not_(None, ""), tenant=tenant, roles=[interview_role]
    )
    if len(screeners) == 0:
        return {"first_name": "No Interviewer Available", "booking_link": ""}

    records = [
        {
            "first_name": r["first_name"] or "Interviewer",
            "booking_link": r["booking_link"],
        }
        for r in screeners
    ]
    # Shuffle the records list
    random.shuffle(records)
    return random.choice(records)


def get_finances(tenant_id, user, usermap=None, permissions=None, tenant=None):
    """Get financial data from the tenant table."""
    tenant, usermap, permissions = validate_user(
        tenant_id, user, usermap, permissions, tenant
    )

    if "see_finances" not in permissions:
        return {}

    data = app_tables.finances.get(tenant=tenant)
    return {
        "rev_12": data["rev_12"] or 0,
        "budgets": data["budgets"] or {},
        "rev_12_active": data["rev_12_active"] or 0,
    }


# def get_forumlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
#     """Get link to forum."""
#     tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
#     return tenant['discourse_url']


# def get_discordlink(tenant_id, user, usermap=None, permissions=None, tenant=None):
#     tenant, usermap, permissions = validate_user(tenant_id, user, usermap, permissions, tenant)
#     if 'see_forum' in permissions:
#         return tenant['discord_invite']
#     return ''


def get_roles(tenant_id, user, usermap=None, permissions=None, tenant=None):
    from .helpers import role_row_to_dict

    tenant, usermap, permissions = validate_user(
        tenant_id, user, usermap, permissions, tenant
    )
    if "see_forum" in permissions:
        role_search = app_tables.roles.search(tenant=tenant)

        role_list = [role_row_to_dict(i) for i in role_search]
        return role_list
    return []
