from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox
from idna import valid_label_length

from config import VALID_CAT_SOFTWARES

class CatDropdown(QWidget):
   def __init__(self, label, value, handler):
       super().__init__()

       layout = QVBoxLayout()
       message = QLabel(f'{label}: ')
       layout.addWidget(message)

       dropdown = QComboBox()
       dropdown.addItem('---select software--')
       for software in VALID_CAT_SOFTWARES:
           dropdown.addItem(software)

       if value in VALID_CAT_SOFTWARES:
           dropdown.setCurrentText(value)
       else:
           dropdown.setCurrentText(None)
       dropdown.currentTextChanged.connect(handler)
       layout.addWidget(dropdown)

       self.setLayout(layout)

