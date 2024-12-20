import anvil.http
import anvil.server

# https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions_create
if (
    anvil.server.get_app_origin() is None
    or "debug" in anvil.server.get_app_origin()
    or "test" in anvil.server.get_app_origin()
    or "dizzy-" in anvil.server.get_api_origin()
):
    TOKEN_URL = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    SUBSCRIPTION_URL = "https://api-m.sandbox.paypal.com/v1/billing/subscriptions"
    VERIFY_URL = (
        "https://api.sandbox.paypal.com/v1/notifications/verify-webhook-signature"
    )
else:
    TOKEN_URL = "https://api.paypal.com/v1/oauth2/token"
    SUBSCRIPTION_URL = "https://api.paypal.com/v1/billing/subscriptions"
    VERIFY_URL = "https://api.paypal.com/v1/notifications/verify-webhook-signature"


def get_paypal_auth(client_id, client_secret, verbose=False):
    import json

    try:
        auth_response = anvil.http.request(
            TOKEN_URL,
            method="POST",
            username=client_id,
            password=client_secret,
            headers={"Accept": "application/json"},
            data={"grant_type": "client_credentials"},
        )
        # print(auth_response.get_bytes())
        auth_response = json.loads(auth_response.get_bytes().decode("utf-8"))
        if verbose:
            print(auth_response)
        access_token = auth_response["access_token"]
        return access_token
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")
        print(e.content.get_bytes())
        raise anvil.http.HttpError(e.status, e.content)


def verify_webhook(
    client_id,
    client_secret,
    webhook_id,
    headers,
    body,
    access_token=None,
    verbose=False,
):
    access_token = access_token or get_paypal_auth(client_id, client_secret)

    new_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    data = {
        "auth_algo": headers["paypal-auth-algo"],
        "cert_url": headers["paypal-cert-url"],
        "transmission_id": headers["paypal-transmission-id"],
        "transmission_sig": headers["paypal-transmission-sig"],
        "transmission_time": headers["paypal-transmission-time"],
        "webhook_id": webhook_id,
        "webhook_event": body,
    }
    response = anvil.http.request(
        VERIFY_URL, headers=new_headers, method="POST", data=data, json=True
    )
    if verbose:
        print(response)
    if response["verification_status"] == "SUCCESS":
        return True
    else:
        print(VERIFY_URL)
        print(client_id)
        print(client_secret)
        print(webhook_id)
        print(headers)
        print(body)
        return False


def create_subscription(
    client_id,
    client_secret,
    plan_id,
    return_url,
    cancel_url,
    access_token=None,
    verbose=False,
):
    """Create a new paypal subscription using a plan_id."""
    access_token = access_token or get_paypal_auth(client_id, client_secret)

    try:
        response = anvil.http.request(
            SUBSCRIPTION_URL,
            method="POST",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            data={
                "plan_id": plan_id,
                "application_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
            },
            json=True,
        )
        if verbose:
            print(response)
        return response
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")
        raise anvil.http.HttpError(e.status, e.content)


def get_subscription(
    client_id, client_secret, subscription_id, verbose=False, access_token=None
):
    """Get all info for a subscription id."""
    import requests

    access_token = access_token or get_paypal_auth(client_id, client_secret)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{SUBSCRIPTION_URL}/{subscription_id}", headers=headers)
    if verbose:
        print(response.json())
    return response.json()


def cancel_subscription(
    client_id,
    client_secret,
    subscription_id,
    reason="Cancelled",
    access_token=None,
    verbose=False,
):
    """Cancel a PayPal subscription."""
    import json

    access_token = access_token or get_paypal_auth(client_id, client_secret)

    try:
        response = anvil.http.request(
            f"{SUBSCRIPTION_URL}/{subscription_id}/cancel",
            method="POST",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            data=json.dumps({"reason": f"{reason}"}),
        )
        if verbose:
            print(response)
        return response
    except anvil.http.HttpError as e:
        print(f"Error {e.status} {e.content}")
        print(e.content.get_bytes())
        raise anvil.http.HttpError(e.status, e.content)


def get_subscription_id(body):
    return body["resource"]["id"]
