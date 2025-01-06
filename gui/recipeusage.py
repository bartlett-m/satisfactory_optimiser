'''Widget for displaying detail about a recipes usage in the solution'''
from numbers import Rational

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QFrame, QSizePolicy

from satisfactoryobjects.recipehandler import recipes
from utils.directionenums import Direction


class RecipeUsage(QFrame):
    def __init__(
        self,
        recipe_id: str,
        number_used: Rational,
        *args,
        **kwargs
    ) -> None:
        super(RecipeUsage, self).__init__(*args, **kwargs)

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.setLineWidth(1)

        layout = QGridLayout()

        recipe = recipes[recipe_id]

        title_widget = QLabel(
            recipe.user_facing_name,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )
        layout.addWidget(title_widget, 0, 0, 1, 4)

        layout.addWidget(QLabel('Number of machines'), 1, 0, 1, 2)
        machine_number_label = QLabel(str(float(number_used)), alignment=Qt.AlignmentFlag.AlignHCenter)
        machine_number_label.setToolTip(str(number_used))
        layout.addWidget(machine_number_label, 2, 0, 1, 2)

        layout.addWidget(QLabel('Total power consumption'), 1, 2, 1, 2)

        power_flow_rate = recipe.calc_power_flow_rate(Direction.IN)

        layout.addWidget(QLabel(str(power_flow_rate * number_used) + ' MW', alignment=Qt.AlignmentFlag.AlignHCenter), 2, 2, 1, 2)

        layout.addWidget(QLabel('Item consumption rate:', alignment=Qt.AlignmentFlag.AlignHCenter), 3, 0, 1, 2)
        layout.addWidget(QLabel('Item production rate:', alignment=Qt.AlignmentFlag.AlignHCenter), 3, 2, 1, 2)

        flow_rates_in = recipe.calc_resource_flow_rate(
            calculated_direction=Direction.IN,
            positive_direction=Direction.IN
        )

        for idx, flow_rate in enumerate(flow_rates_in):
            layout.addWidget(QLabel(flow_rate.item.user_facing_name), 4 + idx, 0)
            layout.addWidget(QLabel(str(flow_rate.amount * number_used) + '/min', alignment=Qt.AlignmentFlag.AlignRight), 4 + idx, 1)

        flow_rates_out = recipe.calc_resource_flow_rate(
            calculated_direction=Direction.OUT
        )

        for idx, flow_rate in enumerate(flow_rates_out):
            layout.addWidget(QLabel(flow_rate.item.user_facing_name), 4 + idx, 2)
            layout.addWidget(QLabel(str(flow_rate.amount * number_used) + '/min', alignment=Qt.AlignmentFlag.AlignRight), 4 + idx, 3)

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
