'''Widget to provide a quick overview of the solution'''

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget, QSizePolicy, QScrollArea


class SolutionQuickOverview(QWidget):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(SolutionQuickOverview, self).__init__(*args, **kwargs)

        layout = QGridLayout()

        requested_item_production_view_layout_container = QWidget()

        self.requested_item_production_view_layout = QGridLayout(
            requested_item_production_view_layout_container
        )

        # static labels

        layout.addWidget(
            QLabel(
                'Solution Overview',
                alignment=Qt.AlignmentFlag.AlignHCenter
            ),
            0, 0, 1, 4
        )

        layout.addWidget(
            QLabel('Objective variable value:'),
            1, 0
        )

        layout.addWidget(
            QLabel('Total power consumption:'),
            1, 2
        )

        layout.addWidget(
            QLabel(
                'Target item production rates:',
                alignment=Qt.AlignmentFlag.AlignHCenter
            ),
            2, 0, 1, 4
        )

        requested_item_production_view_container = QScrollArea()
        requested_item_production_view_container.setWidget(
            requested_item_production_view_layout_container
        )
        requested_item_production_view_container.setWidgetResizable(True)

        layout.addWidget(
            requested_item_production_view_container,
            3, 0, 1, 4
        )

        self.setLayout(layout)
