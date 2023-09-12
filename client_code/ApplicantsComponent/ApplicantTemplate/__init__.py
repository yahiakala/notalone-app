from ._anvil_designer import ApplicantTemplateTemplate
from anvil import *
import anvil.server


class ApplicantTemplate(ApplicantTemplateTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)


    def btn_accept_click(self, **event_args):
        """This method is called when the button is clicked"""
        _ = anvil.server.call('reassign_roles', self.item, {'auth_profile': True, 'auth_booking': False})
        self.parent.raise_event('x-refresh')

    def btn_reject_click(self, **event_args):
        """This method is called when the button is clicked"""
        _ = anvil.server.call('reassign_roles', self.item, {'auth_booking': False})
        self.parent.raise_event('x-refresh')
