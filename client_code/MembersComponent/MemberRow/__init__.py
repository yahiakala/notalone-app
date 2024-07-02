from ._anvil_designer import MemberRowTemplate
from anvil import *


class MemberRow(MemberRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        if self.item:
            self.link_email.text = self.item['email']
            self.link_name.text = self.item['first_name'] + ' ' + self.item['last_name']
            if self.item['last_login']:
                self.link_last_login.text = 'Last login: ' + self.item['last_login'].strftime('%Y-%m-%d')
            else:
                self.link_last_login.text = 'Never'
            if self.item['signed_up']:
                self.link_signed_up.text = 'Signed up: ' + self.item['signed_up'].strftime('%Y-%m-%d')
            else:
                self.link_signed_up.text = 'Manual'
        else:
            self.link_email.role = 'skeleton'
            self.link_name.role = 'skeleton'
            self.link_last_login.role = 'skeleton'
            self.link_signed_up.role = 'skeleton'
        # Any code you write here will run before the form opens.

    def link_email_click(self, **event_args):
        """This method is called when the link is clicked"""
        pass
