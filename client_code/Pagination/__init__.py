import anvil.server
from anvil import *

from .. import tablemod
from ..utils import print_timestamp
from ._anvil_designer import PaginationTemplate


class Pagination(PaginationTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    @property
    def data_grid(self):
        return self._data_grid

    @data_grid.setter
    def data_grid(self, value):
        self._data_grid = value

    @property
    def repeating_panel(self):
        return self._repeating_panel

    @repeating_panel.setter
    def repeating_panel(self, value):
        self._repeating_panel = value
        self.refresh_pagination()
        self.fp_pagination.visible = True

    def refresh_pagination(self):
        tablemod.refresh_pagination(self)

    def btn_next_arrow_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_curr_page.visible = False
        self.img_load.visible = True
        with anvil.server.no_loading_indicator:
            tablemod.btn_next_arrow_click(self)
        self.img_load.visible = False
        self.btn_curr_page.visible = True

    def btn_prev_arrow_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            tablemod.btn_prev_arrow_click(self)

    def btn_first_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            tablemod.btn_first_click(self)

    def btn_last_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_curr_page.visible = False
        self.img_load.visible = True
        with anvil.server.no_loading_indicator:
            items = self._repeating_panel.items
            # self._repeating_panel.items = [None] * 3
            _ = items[len(items) - 1]
            # self._repeating_panel.items = items
            tablemod.btn_last_click(self)
        self.img_load.visible = False
        self.btn_curr_page.visible = True

    def btn_prev_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            tablemod.btn_prev_click(self)

    def btn_next_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_curr_page.visible = False
        self.img_load.visible = True
        with anvil.server.no_loading_indicator:
            tablemod.btn_next_click(self)
        self.img_load.visible = False
        self.btn_curr_page.visible = True

    def btn_dots_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            tablemod.set_page(self, int(self.btn_dots_1.text) - 1)

    def btn_dots_2_click(self, **event_args):
        """This method is called when the button is clicked"""
        with anvil.server.no_loading_indicator:
            tablemod.set_page(self, int(self.btn_dots_2.text) - 1)
