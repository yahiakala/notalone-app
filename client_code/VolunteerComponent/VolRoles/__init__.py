from ._anvil_designer import VolRolesTemplate
from anvil import *
import anvil.server
from ... import Global
from .Chipz import Chipz

import datetime as dt


class VolRoles(VolRolesTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.user = Global.user
        self.init_components(**properties)

        self.fp_assigned_to.add_event_handler('x-remove', self.remove_assignment)

        for member in self.item['member']:
            self.fp_assigned_to.add_component(Chipz(item=member))

        self.dd_addmember.items = [
            (i['first_name'] + ' ' + i['last_name'] + ' (' + i['email'] + ')', i['email'])
            for i in self.item['users']
        ]
        if self.item['last_update']:
            self.lbl_last_update.text = 'Last Update: ' + self.item['last_update'].strftime('%Y-%m-%d')

    def last_update(self, **event_args):
        self.item['last_update'] = dt.date.today()
        self.lbl_last_update.text = 'Last Update: ' + self.item['last_update'].strftime('%Y-%m-%d')

    def dd_addmember_change(self, **event_args):
        """This method is called when an item is selected"""
        if self.dd_addmember.selected_value:
            if self.dd_addmember.selected_value not in [i['email'] for i in self.item['member']]:
                member = anvil.server.call('add_role_to_member', self.item['name'], self.dd_addmember.selected_value)
                self.item['member'].append(member)
                self.fp_assigned_to.add_component(Chipz(item=member))
                self.last_update()

    def remove_assignment(self, member_remove, **event_args):
        self.fp_assigned_to.clear()
        self.item['member'] = [i for i in self.item['member'] if member_remove != i]
        self.last_update()
        anvil.server.call('remove_role_from_member', self.item['name'], member_remove['email'])
        for member in self.item['member']:
            self.fp_assigned_to.add_component(Chipz(item=member))

    def fl_handbook_change(self, file, **event_args):
        """This method is called when a new file is loaded into this FileLoader"""
        anvil.server.call('upload_role_guide', self.item['name'], self.fl_handbook.file)

    def btn_guide_click(self, **event_args):
        """This method is called when the button is clicked"""
        link = anvil.server.call('download_role_guide', self.item['name'])
        from anvil.js import window
        window.open(link.get_url(False))
        # anvil.js.window.location.href = link

    def update_role(self, **event_args):
        if self.tb_name.text != self.item['name'] or self.tb_reports_to.text != self.item['reports_to']:
            print(self.item['name'])
            anvil.server.call(
                'update_role', self.item['name'],
                {'name': self.tb_name.text, 'reports_to': self.tb_reports_to.text}
            )
            self.item['name'] = self.tb_name.text
            self.item['reports_to'] = self.tb_reports_to.text