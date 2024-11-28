import anvil.media
import anvil.server
from anvil import *
from anvil_extras import routing

from ...Global import Global
from ._anvil_designer import ReportRowTemplate


class ReportRow(ReportRowTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        if self.item:
            self.lbl_report_name.text = self.item["name"]
            self.lbl_report_name.role = None

    def btn_run_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.btn_run.text = "Running Report..."
        self.btn_run.italic = True
        self.img_report.visible = True
        with anvil.server.no_loading_indicator:
            output = anvil.server.call(self.item["function"], Global.tenant_id)
        self.img_report.visible = False
        self.btn_run.italic = False
        self.btn_run.text = "Download Report"
        if output:
            anvil.media.download(output)
        else:
            routing.alert("This report is empty.")
