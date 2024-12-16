'''Widget for an item'''
from numbers import Rational

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy


class Item(QFrame):
    def __init__(
        self,
        name: str,
        flow_rate: Rational,
        *args,
        **kwargs
    ) -> None:
        super(Item, self).__init__(*args, **kwargs)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        layout = QGridLayout()

        title_widget = QLabel(
            name,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )
        layout.addWidget(title_widget, 0, 0, 1, 3)

        layout.addWidget(QLabel("Item flow rate"), 3, 0)
        layout.addWidget(QLabel(str(flow_rate) + "/min"), 4, 0)

        layout.addWidget(QLabel("Number of machines"), 3, 1)
        layout.addWidget(QLabel("temp hardcoded value"), 4, 1)

        layout.addWidget(QLabel("Power consumption"), 3, 2)
        layout.addWidget(QLabel("temp hardcoded value"), 4, 2)

        # also do image if I can figure out how to load those from the game
        # spoiler: this looks hard, probably remove the placeholder space

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
