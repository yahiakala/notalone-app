import anvil.tables.query as q
from anvil import *

# import anvil.server
# from anvil_extras.logging import TimerLogger
from anvil_extras import routing

from ..Global import Global
from ._anvil_designer import HomeTemplate


@routing.route("", template="Router")
@routing.route("/home", template="Router")
class Home(HomeTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.groups = []
        self.user = Global.user
        self.init_components(**properties)

    def btn_donate_click(self, **event_args):
        """This method is called when the button is clicked"""
        import anvil.js

        if Global.tenant["donate_url"]:
            anvil.js.window.location.href = Global.tenant["donate_url"]
