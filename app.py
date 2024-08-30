import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer

from cat_relay import CatRelay, MESSAGE
from config import Config, Parameters
from settings import Settings


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
        self.connection_label = QLabel("")
        layout.addWidget(self.connection_label)

        # Sync status label
        self.sync_label = QLabel("")
        layout.addWidget(self.sync_label)

        # Buttons area
        button_box = QHBoxLayout()
        layout.addLayout(button_box)

        # Settings button
        setting_button = QPushButton("Settings")
        setting_button.clicked.connect(self.open_settings)
        button_box.addWidget(setting_button)

        connect_button = QPushButton("Connect")
        connect_button.setCheckable(True)
        connect_button.clicked.connect(self.connect_clicked)
        button_box.addWidget(connect_button)

        self.config = Config()
        # Open settings automatically if no config file found
        if not self.config.config_file_full_path:
            self.open_settings()

        # Core function
        self.cat_relay = CatRelay(self.config.params)
        self.auto_connect = False
        if self.auto_connect:
            self.connection_label.setText("Connecting...")
            self.connect_cat_relay()

    def connect_clicked(self, checked):
        if checked:
            self.auto_connect = True
            self.connect_cat_relay()
        else:
            self.auto_connect = False
            self.disconnect_cat_relay()

    def update_params(self, params):
        if isinstance(params, Parameters):
            print('Parameters updated')
            self.config.params = params
            self.config.save_to_file()
            self.cat_relay.set_params(params)
        else:
            print(f'Unknown params object {params}')

    def open_settings(self):
        settings = Settings(self.config.params, self)
        if settings.exec():
            if self.auto_connect:
                self.connection_label.setText("Settings updated. Reconnecting...")
                self.connect_cat_relay()

    def connect_cat_relay(self):
        try:
            self.cat_relay.connect()
            self.connection_label.setText("Connected")
            self.startTimer(self.config.params.sync_interval * 1000)
        except Exception as e:
            print(e)
            if self.auto_connect:
                self.connect_cat_relay_later(e)

    def disconnect_cat_relay(self):
        self.cat_relay.disconnect()
        self.connection_label.setText("Disconnected")

        # TODO: how to stop default timer?


    def connect_cat_relay_later(self, error):
        message = f'{error}: Retry in {self.config.params.reconnect_time} seconds ...'
        self.connection_label.setText(message)
        self.cat_relay = None
        QTimer.singleShot(self.config.params.reconnect_time * 1000, self.connect_cat_relay)

    def timerEvent(self, event):
        try:
            if self.cat_relay:
                result = self.cat_relay.sync()
                if result:
                    self.sync_label.setText(result[MESSAGE])
        except Exception as e:
            self.connect_cat_relay_later(e)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()