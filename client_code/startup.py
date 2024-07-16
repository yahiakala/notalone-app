import anvil.server
from anvil_extras import routing
from .Router import Router
from .Static import Static
from .Global import Global
# from .StaticWide import StaticWide


@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    print('redirect_no_user')
    return "sign"


@routing.redirect(path="app", priority=18, condition=lambda: Global.get_s('tenant') is None and Global.user is not None)
def redirect_no_tenant():
    print('redirect_no_tenant')
    Global.tenant = anvil.server.call('get_tenant_single')
    if Global.get_s('tenant') is None:
        Global.tenant = anvil.server.call('create_tenant_single')

    try:
        Global.tenant_id = Global.tenant.get_id()
    except Exception:
        Global.tenant_id = Global.tenant['id']

    if 'delete_members' in Global.permissions and (Global.tenant['name'] is None or Global.tenant['name'] == ''):
        return 'app/admin'

    return routing.get_url_hash()


@routing.redirect(path="app", priority=17, condition=lambda: Global.get_s('tenant') is not None and 'book_interview' in Global.permissions and 'see_profile' not in Global.permissions)
def redirect_applicant():
    print('redirect_applicant')
    if routing.get_url_hash() == 'app':
        return 'app/apply'
    else:
        return routing.get_url_hash()


hash, pattern, dict = routing.get_url_components()

routing.set_url_hash(hash)

routing.launch()