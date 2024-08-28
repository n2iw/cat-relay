import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer

from cat_relay import CatRelay, MESSAGE
from config import Config
from settings import Settings


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cat Relay")

        layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        self.connection_label = QLabel("Connecting...")
        layout.addWidget(self.connection_label)

        self.sync_label = QLabel("")
        layout.addWidget(self.sync_label)

        setting_button = QPushButton("Settings")
        setting_button.clicked.connect(self.open_settings)
        layout.addWidget(setting_button)

        self.params = Config()
        self.cat_relay = None
        self.connect_cat_relay()

    def update_params(self, params):
        if isinstance(params, Config):
            print('Parameters updated')
            self.params = params
        else:
            print(f'Unknown params object {params}')

    def open_settings(self):
        settings = Settings(self.params, self)
        if settings.exec():
            self.connection_label.setText("Settings updated. Reconnecting...")
            self.connect_cat_relay()

    def connect_cat_relay(self):
        try:
            self.cat_relay = CatRelay(self.params)
            self.cat_relay.connect()
            self.connection_label.setText("Connected")
            self.startTimer(self.params.get_sync_interval() * 1000)
        except Exception as e:
            print(e)
            self.connect_cat_relay_later(e)

    def connect_cat_relay_later(self, error):
        message = f'{error}: Retry in {self.params.get_reconnect_time()} seconds ...'
        self.connection_label.setText(message)
        self.cat_relay = None
        QTimer.singleShot(self.params.get_reconnect_time() * 1000, self.connect_cat_relay)

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