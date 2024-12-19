from anvil import *

from ...utils import print_timestamp
from ._anvil_designer import FilterChipsTemplate


class FilterChips(FilterChipsTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        print_timestamp("FilterChips")
        # print(self.item)
        self.msdd_profession.items = sorted(self.item["profession"])
        self.msdd_profession.selected = self.item["filters"]["profession"]
        self.msdd_author.items = sorted(self.item["author"])
        self.msdd_author.selected = self.item["filters"]["author"]
        self.msdd_language.items = sorted(self.item["language"])
        self.msdd_language.selected = self.item["filters"]["language"]
        self.msdd_note_type.items = sorted(self.item["note_type"])
        self.msdd_note_type.selected = self.item["filters"]["note_type"]

    def btn_clear_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.msdd_author.selected = []
        self.msdd_language.selected = []
        self.msdd_profession.selected = []
        self.msdd_note_type.selected = []

    def btn_confirm_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.raise_event(
            "x-close-alert",
            value={
                "profession": self.msdd_profession.selected,
                "author": self.msdd_author.selected,
                "language": self.msdd_language.selected,
                "note_type": self.msdd_note_type.selected,
            },
        )

    def msdd_language_change(self, **event_args):
        """This method is called when the selected values change"""
        # print(self.msdd_language.selected)
        pass
