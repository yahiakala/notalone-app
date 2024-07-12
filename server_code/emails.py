import anvil.server
import anvil.email
from .helpers import get_users_with_permission


def notify_paid(user_ref, applicant):
    """Notify the screeners that someone paid."""
    print('Sending email.')
    msg_body = f"""
    <p>Hi {user_ref['first_name']}!</p>

    <p>You are getting this message because an applicant: 
    {applicant['first_name'] + ' ' + applicant['last_name']} ({applicant['email']}) has just paid.</p>

    <p>Regards,</p>
    <p>NotAlone App</p>
    """
    anvil.email.send(
        to=user_ref['email'],
        from_address='noreply',
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
        from_address="noreply",
        from_name="noreply",
        subject=f"Welcome to the {tenant['name']} Community!",
        html=msg_body
    )