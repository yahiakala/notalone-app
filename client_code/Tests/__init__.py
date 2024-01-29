from ._anvil_designer import TestsTemplate
from anvil import *
from .. import test_forms, test_server, test_tasks
from anvil_extras import routing

@routing.route('tests')
class Tests(TestsTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.ctests.test_modules = [test_forms, test_server, test_tasks]
        self.ctests.card_roles=['tonal-card', 'elevated-card', 'elevated-card']
        self.ctests.icon_size=30
        self.ctests.btn_role='filled-button'
