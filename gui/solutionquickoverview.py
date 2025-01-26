'''Widget to provide a quick overview of the solution'''

from fractions import Fraction

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget, QSizePolicy, QScrollArea

from satisfactoryobjects.items import Item

from thirdparty.clearlayout import clear_layout


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

        # create and add static labels

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

        # create dynamic labels
        self.objective_variable_value_label = QLabel(
            'Egads, something went awry!  Widget is not initialised properly!'
        )

        self.total_power_consumption_value_label = QLabel(
            'Egads, something went awry!  Widget is not initialised properly!'
        )

        # add dynamic labels
        layout.addWidget(
            self.objective_variable_value_label,
            1, 1
        )

        layout.addWidget(
            self.total_power_consumption_value_label,
            1, 3
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

        self.reset_dynamic_labels()

    def set_total_power_consumption(self, value):
        '''Helper function to set the total power consumption label to a value with the unit appended'''
        self.total_power_consumption_value_label.setText(str(value) + ' MW')

    def set_objective_variable_value(self, value: Fraction):
        '''Helper function to set the objective variable value label and its tooltip'''
        self.objective_variable_value_label.setText(
            str(float(value))
        )
        self.objective_variable_value_label.setToolTip(str(value))

    def reset_dynamic_labels(self):
        '''Resets the dynamic labels for objective variable value and total power consumption'''
        self.objective_variable_value_label.setText('Nothing yet')
        self.objective_variable_value_label.setToolTip(
            'You probably want to go look in the Problem tab'
        )
        self.set_total_power_consumption(0)

    def add_requested_item_production_view_entry(
        self,
        item: Item,
        number_produced: Fraction
    ):
        # If no co-ordinates are specified, QGridLayout.addWidget will
        # automatically assign the next free co-ordinates, going left-to-right
        # and then top-to-bottom.  Unfortunately, there is no way to specify
        # just the column co-ordinate (so that the layout will have the
        # correct number of columns) or to specify the number of columns when
        # the layout is constructed.  So instead, we calculate the current row
        # manually for the number produced.
        self.requested_item_production_view_layout.addWidget(
            QLabel(item.user_facing_name)
        )
        number_produced_label = QLabel(str(float(number_produced)) + '/min')
        number_produced_label.setToolTip(str(number_produced))
        self.requested_item_production_view_layout.addWidget(
            number_produced_label,
            self.requested_item_production_view_layout.rowCount()-1,
            1,
            alignment=Qt.AlignmentFlag.AlignRight
        )

    def reset_all(self):
        self.reset_dynamic_labels()
        clear_layout(self.requested_item_production_view_layout)
