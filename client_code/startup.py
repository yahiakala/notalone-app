import anvil.server
from anvil_extras import routing
from .Router import Router
from .Static import Static
from .Global import Global
# from .StaticWide import StaticWide


Global.my_tenants = anvil.server.call('get_tenant')
if Global.get_s('my_tenants') is None:
    Global.my_tenants = anvil.server.call('create_tenant_single')

Global.tenant_id = Global.my_tenants[0]['tenant_id']
    


@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    print('something')
    return "sign"


@routing.redirect(path="app", priority=18, condition=lambda: Global.my_tenants[0]['name'] is None or Global.my_tenants[0]['Name'] == '')
def redirect_no_tenant2():
    print('redirect2')
    return 'app/admin'


hash, pattern, dict = routing.get_url_components()

routing.set_url_hash(hash)

routing.launch()