import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

from cat_relay import CatRelay
from config import Parameters


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cat Relay")

        self.params = Parameters()
        self.cat_relay = None
        self.connect_cat_relay()

    def connect_cat_relay(self):
        try:
            self.cat_relay = CatRelay(self.params)
            self.cat_relay.connect()
            self.startTimer(self.params.get_sync_interval() * 1000)
        except Exception as e:
            print(e)
            self.connect_cat_relay_later()

    def connect_cat_relay_later(self):
        print(f'Retry in {self.params.get_reconnect_time()} seconds ...')
        self.cat_relay = None
        QTimer.singleShot(self.params.get_reconnect_time() * 1000, self.connect_cat_relay)

    def timerEvent(self, event):
        try:
            if self.cat_relay:
                self.cat_relay.sync()
        except Exception as e:
            self.connect_cat_relay_later()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()