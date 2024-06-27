from ._anvil_designer import StaticLaunchTemplate
from anvil import *
from anvil_extras import routing

from ..Launchpad import Launchpad


@routing.template(path="launch", priority=2, condition=None)
class StaticLaunch(StaticLaunchTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
