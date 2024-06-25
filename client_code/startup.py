from anvil_extras import routing
from .Router import Router
# from .BlankTemplate import BlankTemplate
from .Static import Static
from .Global import Global


@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
@routing.redirect(path="launchpad", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    return "sign"


hash, pattern, dict = routing.get_url_components()

# Loads the template form
routing.set_url_hash(hash)

routing.launch()