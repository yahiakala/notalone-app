from ._anvil_designer import MemberRowTemplate
from anvil import *
from anvil_extras import routing


class MemberRow(MemberRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Only need email, first_name, last_name, last_login, signed_up
        if self.item:
            self.populate_data()

    def populate_data(self, **event_args):
        self.link_email.text = self.item['user']['email']
        first_name = self.item['user']['first_name'] or ''
        last_name = self.item['user']['last_name'] or ''
        self.link_name.text = first_name + ' ' + last_name
        if self.item['user']['last_login']:
            self.link_last_login.text = self.item['user']['last_login'].strftime('%Y-%m-%d')
        else:
            self.link_last_login.text = 'Never'
        if self.item['user']['signed_up']:
            self.link_signed_up.text = self.item['user']['signed_up'].strftime('%Y-%m-%d')
        else:
            self.link_signed_up.text = 'Manual'

        self.link_email.role = None
        self.link_name.role = None
        self.link_last_login.role = None
        self.link_signed_up.role = None

    def link_email_click(self, **event_args):
        """This method is called when the link is clicked"""
        routing.set_url_hash(
            url_pattern='app/memberdetail',
            url_dict={'user_email': self.item['user']['email']}
        )
