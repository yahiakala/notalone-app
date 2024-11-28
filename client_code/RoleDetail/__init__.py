import anvil.server
from anvil import *

# import anvil.http
from anvil_extras import routing

from ..Global import Global
from ._anvil_designer import RoleDetailTemplate


@routing.route("/roledetail", template="Router", url_keys=["role"])
class RoleDetail(RoleDetailTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
        self.rp_files.items = [None, None, None]
        self.rp_files.add_event_handler("x-delete-file", self.delete_file)

    def form_show(self, **event_args):
        """This method is called when the form is shown on the page"""
        with anvil.server.no_loading_indicator:
            self.item = [i for i in Global.roles if i["name"] == self.url_dict["role"]][
                0
            ]

            self.tb_name.text = self.item["name"]
            self.msdd_permissions.items = Global.all_permissions
            self.msdd_permissions.selected = self.item["permissions"]

            self.tb_name.role = "outlined"
            if self.item["can_edit"] and "edit_roles" in Global.permissions:
                self.tb_name.enabled = True
                self.rp_files.items = anvil.server.call(
                    "get_role_guides", Global.tenant_id, self.item["name"]
                )
                self.rp_files.visible = True
                self.fl_add_file.visible = True
                self.btn_save.visible = True
            else:
                self.rp_files.visible = False
                self.tb_name.enabled = False
                self.btn_save.visible = False

    def fl_add_file_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        self.fl_add_file.text = "Uploading..."
        self.fl_add_file.italic = True
        with anvil.server.no_loading_indicator:
            guides = anvil.server.call(
                "upload_role_guide",
                Global.tenant_id,
                self.item["name"],
                self.fl_add_file.file,
            )
            self.rp_files.items = guides
        self.fl_add_file.italic = False
        self.fl_add_file.text = "Add File"
        # routing.clear_cache()

    def btn_back_click(self, **event_args):
        """This method is called when the button is clicked"""
        routing.go_back()

    def msdd_permissions_change(self, **event_args):
        """This method is called when the selected values change"""
        if "edit_roles" in Global.permissions and self.item["can_edit"]:
            pass
        else:
            self.msdd_permissions.selected = self.item["permissions"]

    def btn_save_click(self, **event_args):
        """This method is called when the button is clicked"""
        if "edit_roles" in Global.permissions:
            new_dict = {
                "name": self.tb_name.text,
                "permissions": self.msdd_permissions.selected,
            }
            anvil.server.call(
                "update_role", Global.tenant_id, self.item["name"], new_dict
            )
            self.item["name"] = new_dict["name"]
            self.item["permissions"] = new_dict["permissions"]
            Global.roles = None
            routing.clear_cache()

    def delete_file(self, item, **event_args):
        if "edit_roles" in Global.permissions:
            guides = anvil.server.call(
                "delete_role_guide", Global.tenant_id, self.item["name"], item["name"]
            )
            self.rp_files.items = guides
            # routing.clear_cache()
