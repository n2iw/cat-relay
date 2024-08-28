from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout


class IPInput(QWidget):
   def __init__(self, label, value, handler):
       super().__init__()

       layout = QHBoxLayout()
       message = QLabel(f'{label}: ')
       layout.addWidget(message)

       line = QLineEdit(value)
       line.textChanged.connect(handler)
       layout.addWidget(line)

       self.setLayout(layout)

