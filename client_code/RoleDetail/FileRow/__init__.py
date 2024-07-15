from ._anvil_designer import FileRowTemplate
from anvil import *


class FileRow(FileRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        if self.item:
            self.lbl_name.text = self.item['name']
            self.lbl_name.role = None
            self.file = self.item['file']
        else:
            self.lbl_name.text = ' ' * 50
            self.file = None

    def btn_view_file_click(self, **event_args):
        """This method is called when the button is clicked"""
        if self.file:
            pass
