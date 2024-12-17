from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QDoubleSpinBox,
    QSizePolicy,
    QLayout
)
import functools

from .config_constants import SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS

# CAUTION: this better have been populated by the time Target.__init__()
# starts getting called or it will likely break
from satisfactoryobjects.recipehandler import recipes
# TODO: this should probably actually be from the items
# also TODO: maybe have some way of passing this in to the constructor instead
# of importing it here (since this code seems like it would be useful for
# resource availability as well)


class Constraint():
    # CAUTION: not a real widget - instead a data structure that autogenerates
    # a few widgets
    def __init__(self):
        self.combo_box = QComboBox()
        for recipe_id, recipe in recipes.items():
            self.combo_box.addItem(recipe.user_facing_name, recipe_id)
        # TODO: also add some special targets for power production etc
        self._value = QDoubleSpinBox()
        self._value.setRange(0, float("inf"))
        self._value.setDecimals(
            SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS
        )
        self._value.setSizePolicy(
            QSizePolicy.Policy.MinimumExpanding,
            QSizePolicy.Policy.Minimum
        )
        self.del_button = QPushButton("-")
        self.del_button.setDisabled(True)
        self.right_side_layout = QHBoxLayout()
        self.right_side_layout.addWidget(self._value)
        self.right_side_layout.addWidget(self.del_button)


class ConstraintsWidget(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super(ConstraintsWidget, self).__init__(*args, **kwargs)

        self.layout_ = QFormLayout(self)

    def set_first_del_button_disabled(self, state: bool):
        '''Set the disabled flag on the delete button of the first target'''
        # note that qt prevents the "clicked" signal from firing if a button
        # is disabled so we dont have to check ourselves
        # for first itemAt():
        # item at 0 is the label, item at 1 is the hboxlayout to its right
        self.layout_.itemAt(1).itemAt(1).widget().setDisabled(state)

    def add_constraint(self, constraint: Constraint):
        '''Add a constraint to the widget'''
        if self.layout_.rowCount() == 1:
            # there will be more than one target after adding this one, so
            # re-enable the button of the first target
            self.set_first_del_button_disabled(False)
        # add the target to the layout
        self.layout_.addRow(constraint.combo_box, constraint.right_side_layout)
        # Set the delete callback
        constraint.del_button.clicked.connect(
            functools.partial(
                self.remove_constraint,
                constraint.right_side_layout
            )
        )
        if self.layout_.rowCount() > 1:
            # this is not the only target, so enable its delete button
            constraint.del_button.setDisabled(False)

    def remove_constraint(self, right_side_layout: QLayout):
        '''Callback for the delete button on targets'''
        self.layout_.removeRow(right_side_layout)
        if self.layout_.rowCount() == 1:
            # only one target now remains, so prevent it from being removed
            self.set_first_del_button_disabled(True)
