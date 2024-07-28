import anvil.server
import anvil.email
from .helpers import get_users_with_permission, validate_user


def notify_paid(usermap, membermap):
    """Notify the admins that someone paid."""
    print('Sending email.')
    msg_body = f"""
    <p>Hi {usermap['first_name']}!</p>

    <p>You are getting this message because an applicant: 
    {membermap['first_name'] + ' ' + membermap['last_name']} ({membermap['user']['email']}) has just paid.</p>

    <p>Regards,</p>
    <p>NotAlone App on behalf of {membermap['tenant']['name']}</p>
    """
    anvil.email.send(
        to=usermap['user']['email'],
        from_address=membermap['tenant']['smtp_email'] or 'noreply',
        from_name="NotAlone",
        subject="Applicant Paid",
        html=msg_body
    )


def email_accept_applicant(tenant, email):
    """Send an email to an applicant upon acceptance."""

    msg_body = f"""
    <p>Hi! This is an automated message from the {tenant['name']} community platform.</p>

    <p>Your application to join the group has been accepted!</p>

    <p>Please log into the app for next steps (see link below). Fill out your profile, read the community guidelines, and make the membership payment.</p>

    <p>{anvil.server.get_app_origin()}</p>
    
    <p>Regards,</p>
    <p>{tenant['name']} via the NotAlone Platform.</p>
    """

    screeners = get_users_with_permission(None, 'see_members', tenant)
    screener_list = [i['user']['email'] for i in screeners]
    anvil.email.send(
        to=email,
        bcc=screener_list,
        from_address=tenant['smtp_email'] or "noreply",
        from_name="noreply",
        subject=f"Welcome to the {tenant['name']} Community!",
        html=msg_body
    )


@anvil.server.callable(require_user=True)
def send_test_email(tenant_id, email):
    user = anvil.users.get_user(allow_remembered=True)
    tenant, usermap, permissions = validate_user(tenant_id, user)
    anvil.email.send(
        to=email,
        from_address=tenant['smtp_email'] or 'noreply',
        from_name='notalone',
        subject='test email',
        text='this is a test email'
    )