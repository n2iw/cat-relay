import copy

from PySide6.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox

from gui_components.dropdown import Dropdown
from gui_components.text_input import TextInput
from gui_components.seconds_input import DecimalSecondsInput, WholeSecondsInput
from config import VALID_CAT_SOFTWARES, PLACEHOLDER_SOFTWARE, VALID_SDRS, SDR_PP, N1MM

class Settings(QDialog):
    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.parent_window = parent

        self.params = copy.deepcopy(params)

        self.setWindowTitle("Settings")
        self.setLayout(self.create_layout())

    def create_layout(self):
        layout = QVBoxLayout()

        # SDR type
        layout.addWidget(Dropdown('SDR Software', SDR_PP, VALID_SDRS, SDR_PP, None, disabled=True))

        # SDR IP
        layout.addWidget(TextInput("SDR IP", self.params.sdr_ip, lambda ip: self.params.set_sdr_ip(ip)))
        # SDR Port
        layout.addWidget(TextInput('SDR Port', self.params.sdr_port, lambda port: self.params.set_sdr_port(port)))

        # CAT Software
        layout.addWidget(Dropdown('Radio Control(CAT) Software', self.params.cat_software, VALID_CAT_SOFTWARES, PLACEHOLDER_SOFTWARE, lambda software: self.params.set_cat_software(software)))

        # CAT IP
        layout.addWidget(TextInput('CAT IP', self.params.cat_ip, lambda ip: self.params.set_cat_ip(ip)))
        # CAT Port
        layout.addWidget(TextInput('CAT Port', self.params.cat_port, lambda port: self.params.set_cat_port(port)))

        # Radio Info Port (only show when it's N1MM)
        self.radio_info = TextInput('Radio Info Port', self.params.radio_info_port, lambda port: self.params.set_radio_info_port(port), self.params.cat_software != N1MM)
        layout.addWidget(self.radio_info)

        # Reconnect time
        layout.addWidget(WholeSecondsInput('Reconnect Time', self.params.reconnect_time, 3, 60, 1, lambda time: self.params.set_reconnect_time(time)))
        # Sync time
        layout.addWidget(DecimalSecondsInput('Sync Interval', self.params.sync_interval, 0.05, 5, 0.01, lambda time: self.params.set_sync_interval(time)))

        # Action Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        return layout

    def accept(self):
        if hasattr(self.parent_window, "update_params"):
            if self.params.cat_software == PLACEHOLDER_SOFTWARE:
                print('Please select a CAT Software')
                return
            self.parent_window.update_params(self.params)
        else:
            print("Unknown parent window, do nothing")
        super().accept()
