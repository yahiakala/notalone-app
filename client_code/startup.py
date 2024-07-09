import anvil.server
from anvil_extras import routing
from .Router import Router
from .Static import Static
from .Global import Global
from .StaticWide import StaticWide


Global.my_tenants = anvil.server.call('get_tenant')
if Global.get_s('my_tenants'):
    Global.tenant_id = Global.my_tenants[0]['tenant_id']


@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    print('something')
    return "sign"


@routing.redirect(path="app", priority=19, condition=lambda: Global.get_s('my_tenants') is None and Global.user is not None)
def redirect_no_tenant():
    routing.set_url_hash('staticwide/setup')
    # return "staticwide/setup"


hash, pattern, dict = routing.get_url_components()

routing.set_url_hash(hash)

routing.launch()