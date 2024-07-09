from ._anvil_designer import SetupTemplate
from anvil import *
from ..Global import Global
from anvil_extras import routing


@routing.route('', template='StaticWide')
@routing.route('/setup', template='StaticWide')
@routing.route('/admin', template='Router')
class Setup(SetupTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
