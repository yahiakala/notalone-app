from ._anvil_designer import StaticTemplate
from anvil import *
from anvil_extras import routing

from ..Signin import Signin
from ..Signup import Signup
from ..Sign import Sign
# from ..Launchpad import Launchpad


@routing.template(path='', priority=3, condition=None)
class Static(StaticTemplate):
    def __init__(self, **properties):
        # All other templates need higher priority than this one.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
