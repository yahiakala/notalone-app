from anvil_extras import routing
from .HomeForm import HomeForm

hash, pattern, dict = routing.get_url_components()

# Loads the template form
routing.set_url_hash(pattern)

routing.launch()