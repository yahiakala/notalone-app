import anvil.server
from anvil_extras import routing
from .Router import Router
from .Static import Static
from .Global import Global


Global.tenant_id = anvil.server.call('get_tenant_id')

@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
@routing.redirect(path="launch", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    return "sign"


hash, pattern, dict = routing.get_url_components()

routing.set_url_hash(hash)

routing.launch()