from ._anvil_designer import DaySelectorTemplate
from anvil import *

class DaySelector(DaySelectorTemplate):
    day_of_week = {
        0: 'Mon',
        1: 'Tue',
        2: 'Wed',
        3: 'Thu',
        4: 'Fri',
        5: 'Sat',
        6: 'Sun'
    }
    
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        # Time slots for every hour
        times = [(f'{i}:00'.zfill(5), i) for i in range(24)]
        self.dd_start.items = times
        self.dd_end.items = times[:]
        self.init_components(**properties)

    def cb_dayofweek_change(self, **event_args):
        """This method is called when this checkbox is checked or unchecked"""
        self.refresh_data_bindings()
        
        
