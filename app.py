import sys
from PySide6.QtWidgets import QApplication, QMainWindow

from cat_relay import CatRelay
from config import Parameters


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cat Relay")

        params = Parameters()
        self.cat_relay = CatRelay(params)
        self.startTimer(params.get_sync_interval() * 1000)

    def timerEvent(self, event):
        self.cat_relay.sync()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
app.exec()