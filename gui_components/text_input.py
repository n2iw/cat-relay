from inspect import isfunction

from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout

INTEGER = 'integer'
TEXT = 'text'

class TextInput(QWidget):
    def __init__(self, label, value, handler, visible = True, data_type = TEXT):
        super().__init__()

        self.handler = handler
        self.data_type = data_type

        layout = QHBoxLayout()
        message = QLabel(f'{label}: ')
        layout.addWidget(message)

        self.line = QLineEdit(str(value))
        self.line.textChanged.connect(self.text_changed)
        layout.addWidget(self.line)

        if not visible:
            self.hide()

        self.setLayout(layout)

    def text_changed(self, text):
        if isfunction(self.handler):
            data = text
            if self.data_type == INTEGER:
                data = int(text)
            self.handler(data)

    def set_visibility(self, visible):
        if visible:
            self.show()
        else:
            self.hide()

