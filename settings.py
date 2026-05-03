import copy
import logging

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QDialog, QDialogButtonBox, QLabel, QLineEdit

from gui_components.dropdown import Dropdown
from gui_components.text_input import TextInput, INTEGER
from gui_components.seconds_input import DecimalSecondsInput, WholeSecondsInput
from config import VALID_CAT_SOFTWARES, PLACEHOLDER_SOFTWARE, VALID_SDRS, SDR_PP, N1MM, VALID_LOCATIONS, LOCAL, NETWORK
from utils.log_config import LOG_DIR

logger = logging.getLogger(__name__)


class Settings(QDialog):
    def __init__(self, params, parent=None):
        super().__init__(parent)

        # Set up data
        self.params = params.copy()

        # Set up UI
        self.parent_window = parent
        self.radio_info_widget: TextInput
        self.sdr_ip_widget: TextInput
        self.cat_ip_widget: TextInput
        self.setWindowTitle("Settings")
        self.setLayout(self.create_layout())


        # Connect Signals/Slots
        self.params.sdr_location_changed.connect(self.sdr_location_changed)
        self.params.cat_location_changed.connect(self.cat_location_changed)
        self.params.cat_software_changed.connect(self.cat_software_changed)
        self.params.sdr_software_changed.connect(self.sdr_software_changed)

    def create_layout(self):
        layout = QVBoxLayout()

        # SDR type
        layout.addWidget(Dropdown('SDR Software', self.params.sdr_software, VALID_SDRS, SDR_PP, lambda software: self.params.set_sdr_software(software)))

        # SDR Location
        layout.addWidget(Dropdown("SDR running on", self.params.sdr_location, VALID_LOCATIONS, LOCAL, lambda location: self.params.set_sdr_location(location)))
        # SDR IP
        self.sdr_ip_widget = TextInput("SDR IP", self.params.sdr_ip, lambda ip: self.params.set_sdr_ip(ip), self.params.sdr_location == NETWORK)
        layout.addWidget(self.sdr_ip_widget)
        # SDR Port
        layout.addWidget(TextInput('SDR Port', self.params.sdr_port, lambda port: self.params.set_sdr_port(port), True, INTEGER))

        # CAT Software
        layout.addWidget(Dropdown('Radio Control(CAT) Software', self.params.cat_software, VALID_CAT_SOFTWARES, PLACEHOLDER_SOFTWARE, lambda software: self.params.set_cat_software(software)))
        # CAT Location
        layout.addWidget(Dropdown("CAT running on", self.params.cat_location, VALID_LOCATIONS, LOCAL, lambda location: self.params.set_cat_location(location)))
        # CAT IP
        self.cat_ip_widget = TextInput('CAT IP', self.params.cat_ip, lambda ip: self.params.set_cat_ip(ip), self.params.cat_location == NETWORK)
        layout.addWidget(self.cat_ip_widget)
        # CAT Port
        layout.addWidget(TextInput('CAT Port', self.params.cat_port, lambda port: self.params.set_cat_port(port), True, INTEGER))

        # Radio Info Port (only show when it's N1MM)
        self.radio_info_widget = TextInput('Radio Info Port', self.params.radio_info_port, lambda port: self.params.set_radio_info_port(port), self.params.cat_software == N1MM, INTEGER)
        layout.addWidget(self.radio_info_widget)

        # Reconnect time
        layout.addWidget(WholeSecondsInput('Reconnect Time', self.params.reconnect_time, 3, 60, 1, lambda time: self.params.set_reconnect_time(time)))
        # Sync time
        layout.addWidget(DecimalSecondsInput('Sync Interval', self.params.sync_interval, 0.05, 5, 0.01, lambda time: self.params.set_sync_interval(time)))

        layout.addWidget(QLabel('Logs can be found at:'))
        log_files_line = QLineEdit(str(LOG_DIR))
        log_files_line.setReadOnly(True)
        layout.addWidget(log_files_line)

        # Action Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        return layout

    @Slot(str)
    def sdr_location_changed(self, location):
        logger.info('Received SDR Location signal: %s', location)
        self.sdr_ip_widget.set_visibility(location == NETWORK)

    @Slot(str)
    def cat_location_changed(self, location):
        logger.info('Received CAT Location signal: %s', location)
        self.cat_ip_widget.set_visibility(location == NETWORK)

    @Slot(str)
    def sdr_software_changed(self, software):
        logger.info('Received SDR software signal: %s', software)
        # self.radio_info_widget.set_visibility(software == N1MM)

    @Slot(str)
    def cat_software_changed(self, software):
        logger.info('Received Cat software signal: %s', software)
        self.radio_info_widget.set_visibility(software == N1MM)

    def accept(self):
        if self.parent_window and hasattr(self.parent_window, "update_params"):
            if self.params.cat_software == PLACEHOLDER_SOFTWARE:
                logger.warning('Please select a CAT Software')
                return
            self.parent_window.update_params(self.params)
        else:
            logger.warning('Unknown parent window, do nothing')
        super().accept()
