import logging
import sys
import asyncio
import threading

from utils.log_config import setup_logging

setup_logging()

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QCheckBox
from PySide6.QtCore import QTimer, Qt, Slot

from cat_relay import CatRelay, MESSAGE, CHANGED
from config import Config, Parameters
from settings import Settings

logger = logging.getLogger(__name__)

CONNECT = 'Connect'
DISCONNECT = 'Disconnect'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cat Relay")

        # Basic window setup
        layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Connect status label
        self.connection_label = QLabel("Not connected")
        layout.addWidget(self.connection_label)

        # Sync status label
        self.sync_label = QLabel("")
        layout.addWidget(self.sync_label)

        # Buttons area
        button_box = QHBoxLayout()
        layout.addLayout(button_box)

        # Auto connect checkbox
        auto_connect_button = QCheckBox("Auto Reconnect")
        auto_connect_button.checkStateChanged.connect(self.auto_connect_changed)
        button_box.addWidget(auto_connect_button)

        # Connect button
        self.connect_button = QPushButton(CONNECT)
        self.connect_button.setCheckable(True)
        self.connect_button.setChecked(True)
        self.connect_button.clicked.connect(self.connect_clicked)
        button_box.addWidget(self.connect_button)

        # Settings button
        setting_button = QPushButton("Settings")
        setting_button.clicked.connect(self.open_settings)
        button_box.addWidget(setting_button)

        self.config = Config()
        self.cat_relay = CatRelay(self.config.params)
        self.connect_cat_relay_signals()
        self.sync_thread = None
        self.auto_connect = False

        # Open settings automatically if no config file found
        if not self.config.config_file_full_path:
            self.open_settings()

    def connect_cat_relay_signals(self):
        self.cat_relay.sync_finished.connect(self.handle_sync_finished)
        self.cat_relay.clients_connected.connect(self.handle_clients_connected)
        self.cat_relay.clients_disconnected.connect(self.handle_clients_disconnected)


    def connect_clicked(self, checked):
        if not checked:
            self.connect_button.setText(DISCONNECT)
            self.connect_cat_relay()
        else:
            self.connect_button.setText(CONNECT)
            self.disconnect_cat_relay()

    @Slot()
    def handle_clients_connected(self):
        self.connect_button.setText(DISCONNECT)
        self.connect_button.setChecked(False)
        self.connection_label.setText("Connected")

    @Slot()
    def handle_clients_disconnected(self):
        self.connect_button.setText(CONNECT)
        self.connect_button.setChecked(True)
        self.connection_label.setText("Not connected")
        if self.auto_connect:
            QTimer.singleShot(self.config.params.reconnect_time * 1000, self.handle_auto_connect_timer)

    @Slot(dict)
    def handle_sync_finished(self, result):
        if result:
            if result[CHANGED]:
                sync_msg = result[MESSAGE]
                if sync_msg != self.sync_label.text():
                    self.sync_label.setText(sync_msg)
        else:
            # Clear last message
            if self.sync_label.text() != '':
                self.sync_label.setText("")

    def handle_auto_connect_timer(self):
        if self.auto_connect:
            self.connect_cat_relay()

    def auto_connect_changed(self, state):
        if state == Qt.CheckState.Checked:
            self.auto_connect = True
        else:
            self.auto_connect = False

    def update_params(self, params):
        if isinstance(params, Parameters):
            logger.info('Parameters updated')
            self.config.params = params
            self.config.save_to_file()
            self.cat_relay = CatRelay(self.config.params)
            self.connect_cat_relay_signals()
        else:
            logger.warning('Unknown params object %s', params)

    def open_settings(self):
        # save previous setting and temporarily disable auto connect
        old_auto_connect = self.auto_connect
        self.auto_connect = False

        # disconnect before opens setting window
        self.disconnect_cat_relay()
        settings = Settings(self.config.params, self)
        settings.exec()
        self.auto_connect = old_auto_connect

    def connect_cat_relay(self):
        if not self.sync_thread or not self.sync_thread.is_alive():
            # Create a thread that runs the coroutine
            self.sync_thread = threading.Thread(target=asyncio.run, args=(self.cat_relay.connect_and_run(),))
            self.sync_thread.start()
        else:
            logger.warning('Sync thread is already running')

    def disconnect_cat_relay(self):
        if self.cat_relay:
            self.cat_relay.stop()

        if self.sync_thread:
            self.sync_thread.join()
            self.sync_thread = None



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()