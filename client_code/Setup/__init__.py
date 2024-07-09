from ._anvil_designer import SetupTemplate
from anvil import *
from ..Global import Global
from anvil_extras import routing


@routing.route('/setup', template='StaticWide')
class Setup(SetupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
