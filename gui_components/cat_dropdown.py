from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox

from config import VALID_CAT_SOFTWARES, PLACEHOLDER_SOFTWARE


class CatDropdown(QWidget):
   def __init__(self, label, value, handler):
       super().__init__()

       layout = QVBoxLayout()
       message = QLabel(f'{label}: ')
       layout.addWidget(message)

       dropdown = QComboBox()
       if value not in VALID_CAT_SOFTWARES:
           dropdown.addItem(PLACEHOLDER_SOFTWARE)
           handler(PLACEHOLDER_SOFTWARE)

       for software in VALID_CAT_SOFTWARES:
           dropdown.addItem(software)

       if value in VALID_CAT_SOFTWARES:
           dropdown.setCurrentText(value)

       dropdown.currentTextChanged.connect(handler)
       layout.addWidget(dropdown)

       self.setLayout(layout)

