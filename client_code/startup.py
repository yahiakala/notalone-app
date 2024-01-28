from anvil_extras import routing


hash, pattern, dict = routing.get_url_components()

# Loads the template form
routing.set_url_hash(pattern)

routing.launch()