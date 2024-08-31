from inspect import isfunction

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout


class TextInput(QWidget):
    def __init__(self, label, value, handler, disabled = False):
        super().__init__()

        self.handler = handler

        layout = QHBoxLayout()
        message = QLabel(f'{label}: ')
        layout.addWidget(message)

        self.line = QLineEdit(str(value))
        self.line.textChanged.connect(self.text_changed)
        layout.addWidget(self.line)

        self.line.setDisabled(disabled)

        self.setLayout(layout)

    def text_changed(self, port):
        if isfunction(self.handler):
            self.handler(int(port))

    def set_enabled(self, enabled):
        self.line.setEnabled(enabled)

