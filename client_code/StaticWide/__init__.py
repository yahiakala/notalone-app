from anvil import *
from anvil_extras import routing

from ..Setup import Setup
from ._anvil_designer import StaticWideTemplate


@routing.template(path="staticwide", priority=7, condition=None)
class StaticWide(StaticWideTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
