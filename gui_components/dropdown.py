from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox



class Dropdown(QWidget):
   def __init__(self, label, value, value_list, placeholder, handler, disabled = False):
       super().__init__()

       layout = QVBoxLayout()
       message = QLabel(f'{label}: ')
       layout.addWidget(message)

       dropdown = QComboBox()
       if value not in value_list:
           dropdown.addItem(placeholder)
           handler(placeholder)

       for software in value_list:
           dropdown.addItem(software)

       if value in value_list:
           dropdown.setCurrentText(value)

       dropdown.currentTextChanged.connect(handler)
       layout.addWidget(dropdown)
       dropdown.setDisabled(disabled)

       self.setLayout(layout)

