from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox
from config import DXLAB, N1MM, FLRIG

class CatDropdown(QWidget):
   def __init__(self, label, value, handler):
       super().__init__()

       layout = QVBoxLayout()
       message = QLabel(f'{label}: ')
       layout.addWidget(message)

       dropdown = QComboBox()
       dropdown.addItem(DXLAB)
       dropdown.addItem(N1MM)
       dropdown.addItem(FLRIG)
       dropdown.setCurrentText(value)
       dropdown.currentTextChanged.connect(handler)
       layout.addWidget(dropdown)

       self.setLayout(layout)

