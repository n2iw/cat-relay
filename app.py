import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, \
    QCheckBox
from PySide6.QtCore import QTimer, Qt, Slot

from cat_relay import CatRelay, MESSAGE
from config import Config, Parameters
from settings import Settings

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
        self.cat_relay.connection_state_changed.connect(self.cat_relay_connection_changed)
        self.timer_id = None
        self.auto_connect = False

        # Open settings automatically if no config file found
        if not self.config.config_file_full_path:
            self.open_settings()

        # Core function
        if self.auto_connect:
            self.connection_label.setText("Connecting...")
            self.connect_cat_relay()

    def connect_clicked(self, checked):
        if not checked:
            self.connect_cat_relay()
        else:
            self.disconnect_cat_relay()

    @Slot(bool)
    def cat_relay_connection_changed(self, state):
        # print(f'CAT Relay connection status: {state}')
        # Update button text
        if state:
            self.connect_button.setText(DISCONNECT)
            self.connect_button.setChecked(False)
            if not self.timer_id:
                self.timer_id = self.startTimer(self.config.params.sync_interval * 1000)
        else:
            self.connect_button.setText(CONNECT)
            self.connect_button.setChecked(True)

            # Stop sync timer
            if self.timer_id:
                self.killTimer(self.timer_id)
                self.timer_id = None
            # Reconnect later
            if self.auto_connect:
                message = 'Connection failed, will try connect later'
                print(message)
                print('-' * 40)
                self.connect_cat_relay_later(message)

    def auto_connect_changed(self, state):
        if state == Qt.CheckState.Checked:
            self.auto_connect = True
        else:
            self.auto_connect = False

    def update_params(self, params):
        if isinstance(params, Parameters):
            print('Parameters updated')
            self.config.params = params
            self.config.save_to_file()
            if self.cat_relay:
                self.cat_relay.set_params(params)
        else:
            print(f'Unknown params object {params}')

    def open_settings(self):
        # save previous setting and temporarily disable auto connect
        old_auto_connect = self.auto_connect
        self.auto_connect = False

        # disconnect before opens setting window
        self.disconnect_cat_relay()
        settings = Settings(self.config.params, self)
        settings.exec()
        self.auto_connect = old_auto_connect
        if self.auto_connect and not self.connect_button.isChecked():
            self.connect_cat_relay()

    def connect_cat_relay(self):
        if self.cat_relay:
            result = self.cat_relay.connect_clients()
            if result:
                self.connection_label.setText("Connected")
            else:
                self.connection_label.setText("Connection failed")
        else:
            print("Cat Relay object doesn't exist!")
            sys.exit()

    def disconnect_cat_relay(self):
        if self.cat_relay:
            self.cat_relay.disconnect_clients()
        self.connection_label.setText("Disconnected")

        if self.timer_id:
            self.killTimer(self.timer_id)
            self.timer_id = None


    def connect_cat_relay_later(self, error):
        # Completely disconnect first
        if self.cat_relay:
            self.cat_relay.disconnect_clients()
        message = f'{error}: Retry in {self.config.params.reconnect_time} seconds ...'
        self.connection_label.setText(message)
        QTimer.singleShot(self.config.params.reconnect_time * 1000, self.connect_cat_relay)

    def timerEvent(self, event):
        if self.cat_relay:
            result = self.cat_relay.sync()
            if result:
                sync_msg = result[MESSAGE]
                if sync_msg != self.sync_label.text():
                    self.sync_label.setText(sync_msg)
            else:
                # Clear last message
                self.sync_label.setText("")


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()