from anvil_extras import routing
from .Router import Router
# from .BlankTemplate import BlankTemplate
from .Static import Static
from .Global import Global
from .StaticLaunch import StaticLaunch


@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
@routing.redirect(path="launch", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    return "sign"

@routing.redirect(path="app", priority=20, condition=lambda: Global.get_no_call('tenant_id') is None)
def redirect_no_tenant():
    return "launch"


hash, pattern, dict = routing.get_url_components()

# Loads the template form
routing.set_url_hash(hash)

routing.launch()