from anvil import *
from anvil.js.window import navigator

from ._anvil_designer import SecretViewerTemplate


class SecretViewer(SecretViewerTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        # Any code you write here will run before the form opens.

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        self._secret = value
        self.tb_secret.text = value

    def btn_view_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.disable_buttons()
        self.raise_event("view")
        if self.tb_secret.hide_text:
            self.tb_secret.hide_text = False
            self.btn_view.icon = "fa:eye-slash"
        else:
            self.tb_secret.hide_text = True
            self.btn_view.icon = "fa:eye"
        self.enable_buttons()

    def btn_edit_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.disable_buttons()
        self.raise_event("edit")
        self.tb_secret.hide_text = False
        self.btn_view.icon = "fa:eye-slash"
        self.tb_secret.enabled = True
        self.enable_buttons()

    def btn_reset_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.disable_buttons()
        self.raise_event("reset")  # This needs to generate a new key.
        self.tb_secret.hide_text = False
        self.btn_view.icon = "fa:eye-slash"
        self.tb_secret.enabled = True
        self.tb_secret.text = self._secret
        self.enable_buttons()

    def btn_copy_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.disable_buttons()
        self.raise_event("copy")
        navigator.clipboard.writeText(self._secret)
        self.enable_buttons()

    def disable_buttons(self):
        self.btn_copy.enabled = False
        self.btn_edit.enabled = False
        self.btn_reset.enabled = False
        self.btn_view.enabled = False
        self.btn_cancel.enabled = False
        self.btn_confirm.enabled = False

    def enable_buttons(self):
        self.btn_copy.enabled = True
        self.btn_edit.enabled = True
        self.btn_reset.enabled = True
        self.btn_view.enabled = True
        self.btn_cancel.enabled = True
        self.btn_confirm.enabled = True

    def btn_confirm_click(self, **event_args):
        """This method is called when the button is clicked"""
        self._secret = self.tb_secret.text
        self.btn_cancel.visible = False
        self.btn_confirm.visible = False
        self.tb_secret.enabled = False
        self.tb_secret.hide_text = True
        self.raise_event("change")

    def btn_cancel_click(self, **event_args):
        """This method is called when the button is clicked"""
        self.tb_secret.text = self._secret
        self.btn_cancel.visible = False
        self.btn_confirm.visible = False
        self.tb_secret.enabled = False
        self.tb_secret.hide_text = True

    def tb_secret_change(self, **event_args):
        """This method is called when the text in this text box is edited"""
        if self._secret != self.tb_secret.text:
            self.btn_confirm.visible = True
            self.btn_cancel.visible = True
        else:
            self.btn_confirm.visible = False
            self.btn_cancel.visible = False
