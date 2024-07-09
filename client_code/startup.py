import anvil.server
from anvil_extras import routing
from .Router import Router
from .Static import Static
from .Global import Global

print('hello')

Global.my_tenants = anvil.server.call('get_tenant')
Global.tenant_id = Global.my_tenants[0]['tenant_id']

print('startup')
print(Global.tenant_id)

@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    return "sign"


hash, pattern, dict = routing.get_url_components()

routing.set_url_hash(hash)

routing.launch()