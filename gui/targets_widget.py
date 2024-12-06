from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFormLayout,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QDoubleSpinBox,
    QSizePolicy
)
from .config_constants import SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS


class Target():
    # CAUTION: not a real widget - instead a data structure that autogenerates
    # a few widgets
    def __init__(self):
        self.combo_box = QComboBox()
        self._value = QDoubleSpinBox()
        self._value.setRange(0, float("inf"))
        self._value.setDecimals(
            SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS
        )
        self._value.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Minimum
        )
        self._del_button = QPushButton("-")
        self.right_side_group = QWidget()
        right_side_layout = QHBoxLayout()
        right_side_layout.addWidget(self._value)
        right_side_layout.addWidget(self._del_button)
        self.right_side_group.setLayout(right_side_layout)


class TargetsWidget(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super(TargetsWidget, self).__init__(*args, **kwargs)

        self.layout_ = QFormLayout()
        self.setLayout(self.layout_)

    def add_target(self, target: Target):
        self.layout_.addRow(target.combo_box, target.right_side_group)
