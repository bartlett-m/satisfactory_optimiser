from typing import Iterable
from fractions import Fraction
from itertools import filterfalse
import logging
# to log how long pivoting takes
import time

from PySide6.QtWidgets import (
    QTabWidget,
    QMainWindow,
    QWidget,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QFormLayout,
    QPushButton,
    QSizePolicy,
    QFrame,
    QComboBox,
    QHBoxLayout,
    QDoubleSpinBox,
    QGroupBox
)
from PySide6.QtCore import Qt

from thirdparty.flowlayout import FlowLayout

from satisfactoryobjects.basesatisfactoryobject import BaseSatisfactoryObject
from satisfactoryobjects.itemvariabletype import ItemVariableType
from satisfactoryobjects.lookuperrors import RecipeLookupError
# CAUTION: these better have been populated by the time Target.__init__()
# starts getting called or it will likely break
from satisfactoryobjects.recipehandler import recipes
from satisfactoryobjects.itemhandler import items
from satisfactoryobjects.recipelookup import lookup_recipes

from utils.directionenums import Direction

from .config_constants import SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS

from .item import Item
from .constraints_widget import ConstraintsWidget, Constraint

from optimisationsolver.simplex import Tableau, Inequality, ObjectiveEquation, Variable


toplevel_logger = logging.getLogger(__name__)


def make_form_subsection_header(
    subsection_label: str,
    button_label: str = 'Add'
) -> tuple[QHBoxLayout, QPushButton]:
    """Helper function to make the subsection header for a form"""
    subsection_header_layout = QHBoxLayout()
    subsection_header_layout.addWidget(QLabel(subsection_label))
    subsection_header_button = QPushButton(button_label)
    # make the button fill the space not occupied by the label
    subsection_header_button.setSizePolicy(
        QSizePolicy.Policy.MinimumExpanding,
        QSizePolicy.Policy.Fixed
    )
    subsection_header_layout.addWidget(subsection_header_button)
    return (subsection_header_layout, subsection_header_button)


def resource_duplicate_typing_saver(
    unencapsulated_resources: Iterable[str]
) -> Iterable[str]:
    """For each string in the iterable, prepend Desc_ and append _C"""
    return map(
        lambda centre_str: f"Desc_{centre_str}_C",
        unencapsulated_resources
    )


class MainWindow(QMainWindow):
    logger = toplevel_logger.getChild("MainWindow")

    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Satisfactory Optimiser")

        self.tabs = QTabWidget()

        # holds the scroll area and the run optimisation button
        self.problem_layout = QVBoxLayout()
        # seemingly needed to make the scroll area play nice with the flow
        # layout
        solution_layout_container = QWidget()
        # is held within a scroll area instead
        self.solution_layout = FlowLayout(solution_layout_container)
        # why the inconsistency?  because pyside6 just doesnt want to behave
        # and i had to rewrite this entire function

        # make scrollable regions for the contents of the tabs
        problem_form_container = QScrollArea()
        solution_tab_content_widget = QScrollArea()

        # why is the code here so inconsistent and messy?
        # because i moved stuff around until finding an order that wasnt buggy
        # what determines whether pyside6 behaves how i want it to or not will
        # forever be a mystery to me
        # put the flowlayout wrapper widget in the scrollarea
        solution_tab_content_widget.setWidget(solution_layout_container)

        # allow the form to dynamically resize as items are added and remove,
        # rather than squashing new items
        problem_form_container.setWidgetResizable(True)
        solution_tab_content_widget.setWidgetResizable(True)

        # widget to contain the problem form
        problem_form_layout_container = QFrame()
        # was an actual QFormLayout, but this caused some layout issues that a
        # QVBoxLayout fixed
        self.problem_form_layout = QVBoxLayout(problem_form_layout_container)

        # custom widget for production targets
        self.targets_widget = ConstraintsWidget()

        # start with one target
        self.targets_widget.add_constraint(Constraint(items))

        # create the header for the production targets section
        (
            targets_subsection_header,
            add_target_button
        ) = make_form_subsection_header(
            'Targets'
        )
        # setup the callback to add new targets
        add_target_button.clicked.connect(self.add_target)
        # add the subsection header
        self.problem_form_layout.addLayout(targets_subsection_header)
        # add the subsection content
        self.problem_form_layout.addWidget(self.targets_widget)

        # custom widget for resource availability constraints
        self.resource_availability_constraints_widget = ConstraintsWidget()

        # start with one resource availability constraint
        # ore nodes present in all tested versions of the docs file
        # iron, caterium, copper, limestone, coal, quartz, sulfur, uranium,
        # bauxite
        for resource in resource_duplicate_typing_saver(
            [
                "OreIron",
                "OreCopper",
                "Stone",  # Limestone
                "Coal",
                "OreGold",  # Caterium
                "Sulfur",
                "RawQuartz",
                "OreBauxite",
                "OreUranium"
            ]
        ):
            # these resources require no special checks, so don't bother with
            # the dictionary lookup
            self.resource_availability_constraints_widget.add_constraint(
                Constraint(items, resource)
            )
        # final ore node: SAM - requires special handling for version
        # differences in the docs file
        try:
            self.resource_availability_constraints_widget.add_constraint(
                # SAM (previously SAM ore)
                # Although present before 1.0, it doesnt seem to appear in
                # docs.json before then.  Since it wasnt possible to automate
                # at that time (nodes would run out until save reload) and no
                # use was yet implemented, it is more sensible to just ignore
                # it.
                # try-except with a lookup from the actual items dictionary to
                # detect if the docs file is pre or post 1.0
                Constraint(items, items["Desc_SAM_C"])
            )
        except KeyError:
            # pre 1.0 docs file, no SAM ore loaded
            pass
        # fluids
        for resource in resource_duplicate_typing_saver(
            [
                "Water",
                "LiquidOil",  # Crude oil
                "NitrogenGas"
            ]
        ):
            # again, these resources require no special checks, so don't
            # bother with the dictionary lookup
            self.resource_availability_constraints_widget.add_constraint(
                Constraint(items, resource)
            )

        # create the header for the resource availability section
        (
            resource_availability_subsection_header,
            add_resource_availability_data_button
        ) = make_form_subsection_header(
            'Resource Availability'
        )
        # setup the callback to add new constraints
        add_resource_availability_data_button.clicked.connect(
            self.add_resource_availability_constraint
        )
        # add the subsection header
        self.problem_form_layout.addLayout(
            resource_availability_subsection_header
        )
        # add the subsection content
        self.problem_form_layout.addWidget(
            self.resource_availability_constraints_widget
        )

        # header for the weightings widget has no add button
        # since there are few weightings
        # FIXME: maybe use a groupbox?  would look inconsistent though
        self.problem_form_layout.addWidget(QLabel("Weightings"))

        self.weightings_form = QFormLayout()

        self.power_usage_spin_box = QDoubleSpinBox()

        for weight_setting_spin_box in [
            self.power_usage_spin_box
        ]:
            weight_setting_spin_box.setRange(
                float("-inf"),
                float("inf")
            )
            weight_setting_spin_box.setDecimals(
                SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS
            )

        self.weightings_form.addRow("Power usage", self.power_usage_spin_box)

        # possible FIXME: maybe encapsulate the QFormLayout in a QWidget to
        # get a more consistent look with the margins
        self.problem_form_layout.addLayout(self.weightings_form)

        # put the layout container widget in the scroll area
        problem_form_container.setWidget(problem_form_layout_container)

        # add the scroll area to the tab layout
        self.problem_layout.addWidget(problem_form_container)
        # create the run button
        run_optimisation_button = QPushButton("Run Optimisation")
        # and connect the clicked signal to the appropriate slot
        run_optimisation_button.clicked.connect(self.run_optimisation)
        # add the run button outside the scroll area but within the tab layout,
        # so it is always visible
        self.problem_layout.addWidget(run_optimisation_button)

        # make a widget to hold the layout of the problem tab
        problem_tab_content_widget = QWidget()
        # and add the layout to it
        problem_tab_content_widget.setLayout(self.problem_layout)

        # add the tabs
        self.tabs.addTab(problem_tab_content_widget, "Problem")
        self.tabs.addTab(solution_tab_content_widget, "Solution")

        # testing
        self.solution_layout.addWidget(Item("test1", 1))
        self.solution_layout.addWidget(Item("test2", 2))
        self.solution_layout.addWidget(Item("test3", 3))

        # set the tab layout as the main widget
        self.setCentralWidget(self.tabs)

    def add_target(self):
        self.targets_widget.add_constraint(Constraint(items))

    def add_resource_availability_constraint(self):
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items)
        )

    def run_optimisation(self):
        # FIXME: this is a stub as the actual functionality hasnt yet been
        # implemented
        # currently being used to trigger debug functionality
        test = self.targets_widget.layout_.itemAt(0).widget()
        print(test.currentData())
        print(test.currentText())
        print(test.currentIndex())
        print(self.targets_widget.get_constraints())

        for target_item, target_production_rate in self.targets_widget.get_constraints():
            print(items[target_item])
            print(target_production_rate)

        manually_set_constraints: set[Item] = set()
        problem_constraints: list[Inequality] = list()

        # add the constraints for the input items
        for available_resource, available_resource_rate in self.resource_availability_constraints_widget.get_constraints():
            number_per_minute = available_resource_rate
            if number_per_minute == 0:
                MainWindow.logger.warning(
                    'Constraint for item with id '
                    f'{available_resource}'
                    ' is set to zero!  Skipping.'
                )
            else:
                resource = items[available_resource]
                manually_set_constraints.add(resource)
                cons = Inequality([Variable(ItemVariableType(resource, True), 1)], Fraction(number_per_minute))
                print(cons)
                problem_constraints.append(cons)

        """print('start prefilter')
        start_time = time.time_ns()
        # resources that no recipe makes and we dont have a manual input of
        unobtainable_resources: set[Item] = set()
        infeasible_recipes: set[str] = set()
        while True:
            previous_unobtainable_resources = frozenset(unobtainable_resources)
            previous_infeasible_recipes = frozenset(infeasible_recipes)

            for resource in filterfalse(
                lambda i: i in manually_set_constraints | unobtainable_resources,
                items.values()
            ):
                try:
                    producing_recipes = lookup_recipes(resource)
                    found_feasible_recipe = False
                    for recipe in filterfalse(
                        lambda r: r.internal_class_identifier in infeasible_recipes,
                        producing_recipes
                    ):
                        recipe_is_feasible = True
                        for dependency in recipe.dependencies:
                            if dependency.item in unobtainable_resources:
                                recipe_is_feasible = False
                                MainWindow.logger.debug(
                                    'Recipe with id '
                                    f'{recipe.internal_class_identifier}'
                                    ' marked as infeasible due to using '
                                    'unobtainable item with id '
                                    f'{dependency.item.internal_class_identifier}'
                                )
                                infeasible_recipes.add(recipe.internal_class_identifier)
                                break
                        if recipe_is_feasible:
                            found_feasible_recipe = True
                    if not found_feasible_recipe:
                        MainWindow.logger.debug(
                            'Item with id '
                            f'{resource.internal_class_identifier}'
                            ' has no feasible recipes, marking as unobtainable'
                        )
                        unobtainable_resources.add(resource)
                except RecipeLookupError:
                    MainWindow.logger.debug(
                        'No recipes produce item with id '
                        f'{resource.internal_class_identifier}'
                        ', marking as unobtainable'
                    )
                    unobtainable_resources.add(resource)

            if unobtainable_resources == previous_unobtainable_resources and infeasible_recipes == previous_infeasible_recipes:
                break
        end_time = time.time_ns()
        print('end prefilter')
        print((end_time-start_time)/(10**9))"""

        # add the constraints for the absolute numbers of items
        for resource in items.values():
            constraint_variables: list[Variable] = [Variable(ItemVariableType(resource, False), 1)]
            # if a manual input of this resource exists, add it to the constraint
            if resource in manually_set_constraints:
                constraint_variables.append(Variable(ItemVariableType(resource, True), -1))
            # add data on the recipes producing this item
            try:
                producing_recipes = lookup_recipes(resource)
                for recipe in producing_recipes:
                    for flow_data in recipe.calc_resource_flow_rate(
                        calculated_direction=Direction.OUT,
                        positive_direction=Direction.IN
                    ):
                        if flow_data.item == resource:
                            # using recipes class identifier string instead of
                            # the recipe object itself as recipe is unhashable
                            constraint_variables.append(Variable(recipe.internal_class_identifier, Fraction(flow_data.amount)))
            except RecipeLookupError:
                MainWindow.logger.debug(
                    'No recipes produce item with id '
                    f'{resource.internal_class_identifier}'
                    ', only adding data about manual input'
                )

            cons = Inequality(constraint_variables, 0)
            problem_constraints.append(cons)

        # add the constraints for the recipes
        for resource in items.values():
            constraint_variables: list[Variable] = [Variable(ItemVariableType(resource, False), -1)]
            try:
                for recipe in lookup_recipes(resource, True):
                    for flow_data in recipe.calc_resource_flow_rate(
                        calculated_direction=Direction.IN,
                        positive_direction=Direction.IN
                    ):
                        if flow_data.item == resource:
                            # see previous note: recipe is unhashable
                            constraint_variables.append(Variable(recipe.internal_class_identifier, Fraction(flow_data.amount)))
                if len(constraint_variables) == 1:
                    MainWindow.logger.debug(
                        'No feasible recipe consumes item with id '
                        f'{resource.internal_class_identifier}'
                        ', not adding usage constraint'
                    )
                else:
                    problem_constraints.append(Inequality(constraint_variables, 0))
            except RecipeLookupError:
                MainWindow.logger.debug(
                    'No recipes consume item with id '
                    f'{resource.internal_class_identifier}'
                    ', not adding usage constraint'
                )

        # add the objectives and their weights
        # TODO: make this not be a stub
        problem_constraints.append(ObjectiveEquation([Variable(ItemVariableType(items["Desc_IronIngot_C"], False), -1)]))

        print(len(problem_constraints))

        t = Tableau(
            problem_constraints
        )

        print(t.get_variable_values())

        print('start pivot')
        start_time = time.time_ns()
        t.pivot_until_done()
        end_time = time.time_ns()
        print('end pivot')
        print((end_time-start_time)/(10**9))
        print(t.get_variable_values())
