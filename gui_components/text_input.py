from inspect import isfunction

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout


class TextInput(QWidget):
    def __init__(self, label, value, handler, disabled = False):
        super().__init__()

        self.handler = handler

        layout = QHBoxLayout()
        message = QLabel(f'{label}: ')
        layout.addWidget(message)

        line = QLineEdit(str(value))
        line.textChanged.connect(self.port_changed)
        layout.addWidget(line)

        line.setDisabled(disabled)

        self.setLayout(layout)

    def port_changed(self, port):
        if isfunction(self.handler):
            self.handler(int(port))

