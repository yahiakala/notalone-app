import anvil.secrets
import anvil.server
import anvil.tables.query as q
import anvil.users
from anvil.tables import app_tables

from .emails import notify_paid
from .helpers import (
    get_users_with_permission,
    upsert_role,
    usermap_row_to_dict,
    validate_user,
)
from .paypal import (
    cancel_subscription,
    create_subscription,
    get_subscription,
    get_subscription_id,
    verify_webhook,
)


def get_paypal_credentials_and_verify(usermap, headers, body):
    """Get PayPal credentials and verify webhook."""
    client_id = anvil.secrets.decrypt_with_key(
        "encryption_key", usermap["tenant"]["paypal_client_id"]
    )
    client_secret = anvil.secrets.decrypt_with_key(
        "encryption_key", usermap["tenant"]["paypal_secret"]
    )
    webhook_id = anvil.secrets.decrypt_with_key(
        "encryption_key", usermap["tenant"]["paypal_webhook_id"]
    )

    if not verify_webhook(client_id, client_secret, webhook_id, headers, body):
        print("Webhook not verified.")
        raise Exception("Webhook verification failed")
    print("Webhook verified.")

    return client_id, client_secret, webhook_id


@anvil.server.callable(require_user=True)
def create_sub(tenant_id, plan_id):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    client_id = anvil.secrets.decrypt_with_key(
        "encryption_key", tenant["paypal_client_id"]
    )
    client_secret = anvil.secrets.decrypt_with_key(
        "encryption_key", tenant["paypal_secret"]
    )

    # TODO: add tenant id to the return urls and route the app properly
    return_url = anvil.server.get_app_origin() + "/payment-success"
    cancel_url = anvil.server.get_app_origin() + "/payment-cancel"
    response = create_subscription(
        client_id, client_secret, plan_id, return_url, cancel_url
    )

    plan = [i for i in tenant["paypal_plans"] if i["id"] == plan_id][0]

    usermap["fee"] = plan["amt"]
    usermap["paypal_sub_id"] = response["id"]
    membermap = usermap_row_to_dict(usermap)
    if "see_members" not in permissions:
        membermap["notes"] = ""

    return membermap, response["links"][0]["href"]


@anvil.server.callable(require_user=True)
def cancel_user_subscription(tenant_id, email):
    """Cancel a user's PayPal subscription."""
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)

    # Check if user has permission to cancel subscription
    if email != user["email"] and "edit_members" not in permissions:
        raise Exception(
            "You don't have permission to cancel other users' subscriptions"
        )

    # Get the target user and validate
    target_user = app_tables.users.get(email=email)
    if not target_user:
        raise Exception("User not found")

    # Get the membermap for the target user
    _, membermap, _ = validate_user(tenant_id, target_user)
    if not membermap or not membermap["paypal_sub_id"]:
        raise Exception("No active subscription found")

    client_id = anvil.secrets.decrypt_with_key(
        "encryption_key", tenant["paypal_client_id"]
    )
    client_secret = anvil.secrets.decrypt_with_key(
        "encryption_key", tenant["paypal_secret"]
    )

    # Cancel the subscription with PayPal
    cancel_subscription(client_id, client_secret, membermap["paypal_sub_id"])

    result_membermap = usermap_row_to_dict(membermap)
    if "see_members" not in permissions:
        result_membermap["notes"] = ""

    return result_membermap


@anvil.server.route("/payment-success")
def payment_success(**kwargs):
    return anvil.server.HttpResponse(
        302,
        headers={"Location": anvil.server.get_app_origin() + "/#app/paymentconfirm"},
    )


@anvil.server.route("/payment-cancel")
def payment_cancel(**kwargs):
    return anvil.server.HttpResponse(
        302, headers={"Location": anvil.server.get_app_origin() + "/#app/profile"}
    )


@anvil.server.http_endpoint("/capture-sub", methods=["POST"])
def capture_sub(**params):
    headers = anvil.server.request.headers
    print(headers)
    body = anvil.server.request.body_json
    raw_body = anvil.server.request.body.get_bytes().decode("utf-8")
    print(raw_body)

    print(body["event_type"])

    # Launch appropriate background task based on event type
    if body["event_type"] == "PAYMENT.SALE.COMPLETED":
        # anvil.server.launch_background_task("update_sale_payment", headers, body)
        billing_agreement_id = body["resource"].get("billing_agreement_id")
        if not billing_agreement_id:
            print("No billing agreement ID found in sale event.")
            return anvil.server.HttpResponse(400)
        usermap = app_tables.usermap.get(paypal_sub_id=billing_agreement_id)
        if not usermap:
            print("Did not find user.")
            return anvil.server.HttpResponse(400)
        print(usermap["user"]["email"])
    else:
        # anvil.server.launch_background_task("update_subscription", headers, body)
        sub_id = get_subscription_id(body)
        usermap = app_tables.usermap.get(paypal_sub_id=sub_id)
        if not usermap:
            print("Did not find user.")
            return anvil.server.HttpResponse(400)
        print(usermap["user"]["email"])

    client_id = anvil.secrets.decrypt_with_key(
        "encryption_key", usermap["tenant"]["paypal_client_id"]
    )
    client_secret = anvil.secrets.decrypt_with_key(
        "encryption_key", usermap["tenant"]["paypal_secret"]
    )
    webhook_id = anvil.secrets.decrypt_with_key(
        "encryption_key", usermap["tenant"]["paypal_webhook_id"]
    )

    if not verify_webhook(client_id, client_secret, webhook_id, headers, body):
        print("Webhook not verified.")
        return anvil.server.HttpResponse(400)
    print("Webhook verified.")

    return anvil.server.HttpResponse(200)


@anvil.server.background_task
def update_sale_payment(headers, body):
    """Handle PAYMENT.SALE.COMPLETED webhook events."""
    import datetime as dt

    billing_agreement_id = body["resource"].get("billing_agreement_id")
    if not billing_agreement_id:
        print("No billing agreement ID found in sale event.")
        return
    usermap = app_tables.usermap.get(paypal_sub_id=billing_agreement_id)
    if not usermap:
        print("Did not find user.")
        return
    print(usermap["user"]["email"])

    # Verify webhook again in case of delayed execution
    client_id, client_secret, _ = get_paypal_credentials_and_verify(
        usermap, headers, body
    )

    subscription = get_subscription(client_id, client_secret, usermap["paypal_sub_id"])

    # Update payment expiry from subscription
    if (
        "billing_info" in subscription
        and "next_billing_time" in subscription["billing_info"]
    ):
        next_billing_time = subscription["billing_info"]["next_billing_time"]
        billing_datetime = dt.datetime.strptime(next_billing_time, "%Y-%m-%dT%H:%M:%SZ")
        usermap["payment_expiry"] = billing_datetime.date()


@anvil.server.background_task
def update_subscription(headers, body):
    """Handle subscription-related webhook events."""
    import datetime as dt

    sub_id = get_subscription_id(body)
    usermap = app_tables.usermap.get(paypal_sub_id=sub_id)
    if not usermap:
        print("Did not find user.")
        return
    print(usermap["user"]["email"])

    # Verify webhook again in case of delayed execution
    client_id, client_secret, _ = get_paypal_credentials_and_verify(
        usermap, headers, body
    )

    plan_id = body["resource"]["plan_id"]
    plan = [i for i in usermap["tenant"]["paypal_plans"] if i["id"] == plan_id][0]

    if body["resource"]["status"] == "EXPIRED":
        for role in plan["roles"]:
            # TODO: Test more.
            usermap = upsert_role(usermap, "Approved")
            usermap["roles"] = [i for i in usermap["roles"] if i["name"] != role]
    elif body["resource"]["status"] == "ACTIVE":
        for role in plan["roles"]:
            usermap = upsert_role(usermap, role)
            # only add role if they are approved
            approved_role = app_tables.roles.get(
                name="Approved", tenant=usermap["tenant"]
            )
            if approved_role in usermap["roles"]:
                usermap["roles"] = [
                    i
                    for i in usermap["roles"]
                    if i["name"] not in ["Applicant", "Approved"]
                ]
        # if not usermap["payment_status"] or usermap["payment_status"] != 'ACTIVE':  # yet
        #     notify_admins(usermap)

    usermap["payment_status"] = body["resource"]["status"]
    if "billing_info" in body["resource"]:
        usermap["fee"] = float(
            body["resource"]["billing_info"]["last_payment"]["amount"]["value"]
        )
        if "next_billing_time" in body["resource"]["billing_info"]:
            next_billing_time = body["resource"]["billing_info"]["next_billing_time"]
            billing_datetime = dt.datetime.strptime(
                next_billing_time, "%Y-%m-%dT%H:%M:%SZ"
            )
            usermap["payment_expiry"] = billing_datetime.date()


def notify_admins(usermap):
    screeners = get_users_with_permission(None, "see_members", usermap["tenant"])
    for screener in screeners:
        print("Sending email to : " + screener["user"]["email"])
        notify_paid(screener, usermap)


def calc_rev12():
    for tenant in app_tables.tenants.search():
        tenantfin = app_tables.finances.get(tenant=tenant)
        total_rev = 0
        for user_ref in app_tables.users.search(
            tenant=tenant, fee=q.not_(None), good_standing=True
        ):
            total_rev += user_ref["fee"] * 0.97 - 0.3
        tenantfin["rev_12"] = total_rev
        total_rev = 0
        for user_ref in app_tables.users.search(
            tenant=tenant, fee=q.not_(None), good_standing=True, payment_status="ACTIVE"
        ):
            total_rev += user_ref["fee"] * 0.97 - 0.3
        tenantfin["rev_12_active"] = total_rev
