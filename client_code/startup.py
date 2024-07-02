from anvil_extras import routing
from .Router import Router
# from .BlankTemplate import BlankTemplate
from .Static import Static
from .Global import Global
from .StaticLaunch import StaticLaunch
from anvil_squared.utils import print_timestamp
print_timestamp('Startup')


@routing.redirect(path="app", priority=20, condition=lambda: Global.user is None)
@routing.redirect(path="launch", priority=20, condition=lambda: Global.user is None)
def redirect_no_user():
    return "sign"

@routing.redirect(path="app", priority=20, condition=lambda: Global.get_s('tenant_id') is None)
def redirect_no_tenant():
    return "launch"

hash, pattern, dict = routing.get_url_components()

# Loads the template form
routing.set_url_hash(hash)
print_timestamp('before launch')
routing.launch()
print_timestamp('end startup')