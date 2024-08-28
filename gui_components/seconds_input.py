from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox


class SecondsInputBase(QWidget):
    def __init__(self, label, value, min_value, max_value, step, handler, widget_class):
        super().__init__()

        layout = QHBoxLayout()
        message = QLabel(f'{label}: ')
        layout.addWidget(message)

        slider = widget_class()
        slider.setValue(value)
        slider.setRange(min_value, max_value)
        slider.setSingleStep(step)

        slider.valueChanged.connect(handler)
        layout.addWidget(slider)

        self.setLayout(layout)

class WholeSecondsInput(SecondsInputBase):
    def __init__(self, label, value, min_value, max_value, step, handler):
        super().__init__(label, value, min_value, max_value, step, handler, QSpinBox)

class DecimalSecondsInput(SecondsInputBase):
    def __init__(self, label, value, min_value, max_value, step, handler):
        super().__init__(label, value, min_value, max_value, step, handler, QDoubleSpinBox)
