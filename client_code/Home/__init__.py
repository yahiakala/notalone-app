from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.tables.query as q
# import anvil.server
# from anvil_extras.logging import TimerLogger
from anvil_extras import routing
from ..Global import Global


@routing.route('', template='Router')
@routing.route('/home', template='Router')
class Home(HomeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.groups = []
        self.user = Global.user
        self.init_components(**properties)
