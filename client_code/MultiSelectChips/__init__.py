from anvil import *

from ..utils import print_timestamp
from ._anvil_designer import MultiSelectChipsTemplate
from .Chip import Chip
from .FilterChips import FilterChips


class MultiSelectChips(MultiSelectChipsTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        # self.filters = {'profession': [], 'author': [], 'language': [], 'note_type': []}
        print_timestamp("MultiSelectChips")
        self.init_components(**properties)
        self.fp_chips_left.add_event_handler("x-remove", self.remove_item)
        self._selected = []
        # self._filters = properties['filters'] or {'profession': [], 'author': [], 'language': [], 'note_type': []}

    @property
    def show_save(self):
        print_timestamp("MultiSelectChips: get show_save")
        return self._show_save

    @show_save.setter
    def show_save(self, value):
        print_timestamp("MultiSelectChips: set show_save")
        self._show_save = value
        self.btn_save_apply.visible = value

    @property
    def items(self):
        print_timestamp("MultiSelectChips: get items")
        return self._items

    @items.setter
    def items(self, value):
        print_timestamp("MultiSelectChips: set items")
        print("hello1")
        self._items = value
        self._filters = None
        self.selected = []

    @property
    def selected(self):
        print_timestamp("MultiSelectChips: get selected")
        return self._selected

    @selected.setter
    def selected(self, value):
        print_timestamp("MultiSelectChips: set selected")
        self._selected = value
        if value:
            self._selectable = [i for i in self._items if i not in self._selected]
        else:
            self._selectable = self._items
        self.update_chips()

    @property
    def filters(self):
        print_timestamp("MultiSelectChips: get filters")
        return self._filters

    @filters.setter
    def filters(self, value):
        print_timestamp("MultiSelectChips: set filters")
        self._filters = value
        # print(value)
        # print(self._filters)
        if self._filters:
            self.btn_filter.visible = True
        else:
            self.btn_filter.visible = False

    def update_chips(self, **event_args):
        self.apply_filters()
        self.dd_prompts.items = [(i["key"], i["value"]) for i in self._selectable]
        self.dd_prompts.selected_value = None

        self.fp_chips_left.clear()
        self.fp_chips_left.add_component(self.btn_filter)
        self.fp_chips_left.add_component(self.dd_prompts)
        for prompt in self._selected:
            self.fp_chips_left.add_component(
                Chip(item={"name": prompt["key"], "description": prompt["description"]})
            )

    def remove_item(self, remove, **event_args):
        self.selected = [i for i in self._selected if i["key"] != remove]

    def dd_prompts_change(self, **event_args):
        """This method is called when an item is selected"""
        selected_item = self.dd_prompts.selected_value
        self._selectable = [i for i in self._selectable if i["value"] != selected_item]
        self.selected = self.selected + [
            i for i in self.items if i["value"] == selected_item
        ]

    def btn_save_apply_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.raise_event("save")

    def btn_filter_click(self, **event_args):
        """This method is called when the button is clicked"""
        popup_dict = {
            "filters": self.filters,
            "profession": set([i["categories"]["profession"] for i in self._items]),
            "author": set([i["categories"]["author"] for i in self._items]),
            "language": set([i["categories"]["language"] for i in self._items]),
            "note_type": set([i["categories"]["note_type"] for i in self._items]),
        }
        self.filters = alert(
            FilterChips(item=popup_dict),
            role="view-alert",
            dismissible=False,
            buttons=None,
        )
        # print(self.filters)
        self.apply_filters()

    def apply_filters(self, **event_args):
        print_timestamp("MultiSelectChips: apply_filters")
        if not self._filters:
            return None
        # print(self.filters)
        self.filtered_data = [i for i in self._items if i not in self._selected]
        # print(self.filtered_data[:2])

        if self._filters["profession"]:
            self.filtered_data = [
                i
                for i in self.filtered_data
                if i["categories"]["profession"] in self._filters["profession"]
            ]

        if self._filters["author"]:
            self.filtered_data = [
                i
                for i in self.filtered_data
                if i["categories"]["author"] in self._filters["author"]
            ]

        if self._filters["language"]:
            print_timestamp("filtering language")
            self.filtered_data = [
                i
                for i in self.filtered_data
                if i["categories"]["language"] in self._filters["language"]
            ]

        if self._filters["note_type"]:
            self.filtered_data = [
                i
                for i in self.filtered_data
                if i["categories"]["note_type"] in self._filters["note_type"]
            ]

        self._selectable = self.filtered_data
        self.dd_prompts.items = [(i["key"], i["value"]) for i in self._selectable]
        self.dd_prompts.selected_value = None
