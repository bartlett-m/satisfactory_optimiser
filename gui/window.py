from typing import Iterable
from fractions import Fraction
from itertools import filterfalse
import sys
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
    QGroupBox,
    QApplication,
    QRadioButton,
    QButtonGroup,
    QMessageBox
)
from PySide6.QtCore import Qt, QThreadPool, QSettings

from thirdparty.flowlayout import FlowLayout
from thirdparty.clearlayout import clear_layout

from satisfactoryobjects.basesatisfactoryobject import BaseSatisfactoryObject
from satisfactoryobjects.items import Item
from satisfactoryobjects.itemvariabletype import ItemVariableType, ItemVariableTypes
from satisfactoryobjects.lookuperrors import RecipeLookupError
# CAUTION: these better have been populated by the time Target.__init__()
# starts getting called or it will likely break
from satisfactoryobjects.recipehandler import recipes
from satisfactoryobjects.itemhandler import items
from satisfactoryobjects.recipelookup import lookup_recipes

from utils.directionenums import Direction
from utils.variabletypetags import VariableType

from .config_constants import SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS

from .recipeusage import RecipeUsage
from .constraints_widget import ConstraintsWidget, Constraint
from .simplexworker import SimplexWorker

from optimisationsolver.simplex import Tableau, Inequality, ObjectiveEquation, Variable, SimplexAlgorithmDoneException


toplevel_logger = logging.getLogger(__name__)

failed_notification_backend_imports: set[str] = set()
notification_senders = {
    'null': lambda summary, body: 0
}

try:
    from .notifications import dbus
    notification_senders['dbus'] = dbus.add_notification
except ImportError:
    failed_notification_backend_imports.add('dbus')


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

    def __init__(
        self,
        qt_application_reference: QApplication,
        *args,
        **kwargs
    ) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)

        # save a reference to the QApplication, to allow for events to be
        # processed during a callback (e.g. to disable sections of the UI)
        self.qt_application_reference = qt_application_reference

        self.setWindowTitle("Satisfactory Optimiser")

        self.settings = QSettings()

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

        # holds the scroll area and the apply/revert buttons
        settings_layout = QVBoxLayout()

        # make scrollable regions for the contents of the tabs
        problem_form_container = QScrollArea()
        solution_tab_content_widget = QScrollArea()
        settings_form_container = QScrollArea()

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
        # and same for the settings form
        settings_form_layout_container = QFrame()
        # was an actual QFormLayout, but this caused some layout issues that a
        # QVBoxLayout fixed
        self.problem_form_layout = QVBoxLayout(problem_form_layout_container)

        # custom widget for production targets
        self.targets_widget = ConstraintsWidget()

        # start with one target
        self.targets_widget.add_constraint(Constraint(items, default_value=1))

        # create the header for the production targets section
        (
            targets_subsection_header,
            add_target_button
        ) = make_form_subsection_header(
            'Target weightings'
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
        self.problem_tab_content_widget = QWidget()
        # and add the layout to it
        self.problem_tab_content_widget.setLayout(self.problem_layout)

        # same for the settings
        settings_form_layout = QFormLayout()

        # layout for the notification backend radio buttons
        notification_backend_select_layout = QHBoxLayout()

        if self.settings.value('notifications/backend') is None:
            MainWindow.logger.debug('Creating setting for notification backend')
            self.settings.setValue('notifications/backend', 'null')

        if self.settings.value('notifications/backend') in failed_notification_backend_imports:
            MainWindow.logger.critical(
                'User-configured notification backend with id '
                f'{self.settings.value("notifications.backend")}'
                ' failed to load!  Warning user.'
            )
            error_dialog = QMessageBox(
                QMessageBox.Icon.Critical,
                'Configuration problem',
                f'The selected notification backend failed to load.  Restore default setting for notifications and continue, or quit program for troubleshooting?',
                QMessageBox.StandardButton.RestoreDefaults | QMessageBox.StandardButton.Abort
            )
            response = error_dialog.exec()
            if response == QMessageBox.StandardButton.RestoreDefaults:
                MainWindow.logger.warning(
                    'Repairing configuration: resetting notifications/backend '
                    'to null'
                )
                self.settings.setValue('notifications/backend', 'null')
            else:
                MainWindow.logger.critical('User declined configuration repair.')
                MainWindow.logger.critical('Exiting due to configuration error')
                sys.exit(78)

        self.notification_backend_buttons = {
            'null': (QRadioButton('None'), 'Do not send notifications'),
            'dbus': (QRadioButton('D-Bus'), 'Used on Un*x and Un*x-like systems')
        }

        for button_setting_id, button_tuple in self.notification_backend_buttons.items():
            button_tuple[0].setToolTip(button_tuple[1])
            if button_setting_id in failed_notification_backend_imports:
                button_tuple[0].setDisabled(True)

        notification_backend_select_layout.addWidget(
            self.notification_backend_buttons['null'][0]
        )
        notification_backend_select_layout.addWidget(
            self.notification_backend_buttons['dbus'][0]
        )

        settings_form_layout.addRow('Notification backend:', notification_backend_select_layout)

        settings_form_layout_container.setLayout(settings_form_layout)

        settings_form_container.setWidget(settings_form_layout_container)

        settings_layout.addWidget(settings_form_container)

        apply_settings_button = QPushButton('Apply')
        apply_settings_button.setToolTip('Apply new settings to program and write to file on disk')
        apply_settings_button.clicked.connect(self.write_settings)
        cancel_settings_button = QPushButton('Cancel')
        cancel_settings_button.setToolTip('Discard changes made to settings and reload from file on disk')
        cancel_settings_button.clicked.connect(self.reload_settings)
        settings_button_layout = QHBoxLayout()
        settings_button_layout.addWidget(cancel_settings_button)
        settings_button_layout.addWidget(apply_settings_button)

        settings_layout.addLayout(settings_button_layout)

        settings_tab_content_widget = QWidget()
        settings_tab_content_widget.setLayout(settings_layout)

        # add the tabs
        self.tabs.addTab(self.problem_tab_content_widget, 'Problem')
        self.tabs.addTab(solution_tab_content_widget, 'Solution')
        self.tabs.addTab(settings_tab_content_widget, 'Settings')

        # testing
        # self.solution_layout.addWidget(RecipeUsage("Recipe_IngotIron_C", 2))

        # set the tab layout as the main widget
        self.setCentralWidget(self.tabs)

        self.simplex_worker_thread: SimplexWorker = None

        self.thread_pool = QThreadPool()
        MainWindow.logger.info(
            'Multithreading with a maximum of '
            f'{self.thread_pool.maxThreadCount()}'
            ' threads.'
        )

        # load in the settings from the file
        self.reload_settings()

    def reload_settings(self):
        for button_setting_id, button_tuple in self.notification_backend_buttons.items():
            button_tuple[0].setChecked(button_setting_id == self.settings.value('notifications/backend'))

    def write_settings(self):
        for button_setting_id, button_tuple in self.notification_backend_buttons.items():
            if button_tuple[0].isChecked():
                self.settings.setValue('notifications/backend', button_setting_id)

    def add_target(self):
        self.targets_widget.add_constraint(Constraint(items, default_value=1))

    def add_resource_availability_constraint(self):
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items)
        )

    def closeEvent(self, event):
        if self.simplex_worker_thread is not None:
            self.simplex_worker_thread.cancel_soon()
        return super().closeEvent(event)

    def process_simplex_progress(self, progress: int):
        print(f'Have completed {progress} pivots')

    def process_simplex_terminate(self):
        self.simplex_worker_thread = None
        self.problem_tab_content_widget.setDisabled(False)
        notification_senders[
            self.settings.value('notifications/backend')
        ](
            'Optimisation complete', 'View the results in the Solution tab'
        )

    def process_simplex_result(self, result: list):
        print(result)
        for var_id, var_val in result:
            if var_id.type == VariableType.NORMAL:
                # check for string type
                # source: https://stackoverflow.com/a/4843178
                # [accessed 2025-01-06 at 13:12]
                if isinstance(var_id.name, str) and var_val != 0:
                    self.solution_layout.addWidget(RecipeUsage(var_id.name, var_val))
                    print(f'{var_id.name}: {var_val}')

    def run_optimisation(self):
        # disable the UI in the problem tab (to prevent settings from being
        # overridden as they are being read)
        self.problem_tab_content_widget.setDisabled(True)
        # disabling a widget implicitly disables all its children, and
        # enabling a widget implicitly enables all its children that have not
        # been explicitly disabled, so there is no need to worry about the
        # remove constraint buttons being enabled when they shouldnt be
        # reference for this is https://stackoverflow.com/a/34892529
        # [accessed 2025-01-05 at 13:45]
        # note that it specifically talks about the c++ version of qt5, but it
        # seems to still apply to qt6 (and thus its language bindings)

        # process events (so that the UI disable event is handled)
        self.qt_application_reference.processEvents()

        # clear anything left over in the solution layout from previous runs
        clear_layout(self.solution_layout)
        # make sure that this gets processed
        # FIXME: this doesnt actually work - the deletion only gets processed after the callback is done?
        self.qt_application_reference.processEvents()

        target_weights: list[tuple[str, float]] = self.targets_widget.get_constraints()
        # used to more quickly filter what items need output "virtual recipes"
        # created
        target_items: set[Item] = {
            items[target_weight[0]]
            for target_weight
            in target_weights
        }

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
                cons = Inequality([Variable(ItemVariableType(resource, ItemVariableTypes.MANUAL_INPUT), 1)], Fraction(number_per_minute))
                # print(cons)
                problem_constraints.append(cons)

        # add the constraints for the absolute numbers of items
        for resource in items.values():
            constraint_variables: list[Variable] = [Variable(ItemVariableType(resource, ItemVariableTypes.TOTAL), 1)]
            # if a manual input of this resource exists, add it to the constraint
            if resource in manually_set_constraints:
                constraint_variables.append(Variable(ItemVariableType(resource, ItemVariableTypes.MANUAL_INPUT), -1))
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
            constraint_variables: list[Variable] = [Variable(ItemVariableType(resource, ItemVariableTypes.TOTAL), -1)]
            if resource in target_items:
                # also TODO: put this in the try block somehow, and if the except block is triggered when this condition is met then swap the variable in the objective equation to be of the TOTAL type instead of the OUTPUT type, to keep the tableau smaller
                constraint_variables.append(Variable(ItemVariableType(resource, ItemVariableTypes.OUTPUT), 1))
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
                    ', not adding usage constraint unless target'
                )
                # TODO: with regards to above about putting in the try block: replace this logic with something better
                if len(constraint_variables) == 2:
                    problem_constraints.append(Inequality(constraint_variables, 0))

        # add the objectives and their weights
        problem_constraints.append(ObjectiveEquation([
            Variable(ItemVariableType(items[target_weight[0]], ItemVariableTypes.OUTPUT), target_weight[1] * -1)
            for target_weight
            in target_weights
        ]))

        # print(len(problem_constraints))

        self.simplex_worker_thread = SimplexWorker(problem_constraints)
        self.simplex_worker_thread.signals.result.connect(self.process_simplex_result)
        self.simplex_worker_thread.signals.finished.connect(self.process_simplex_terminate)
        self.simplex_worker_thread.signals.progress.connect(self.process_simplex_progress)

        self.thread_pool.start(self.simplex_worker_thread)

        #t = Tableau(
        #    problem_constraints
        #)

        # print(t.get_variable_values())

        #print('start pivot')
        #start_time = time.time_ns()
        #t.pivot_until_done()
        #end_time = time.time_ns()
        #print('end pivot')
        #print((end_time-start_time)/(10**9))

        # re-enable the UI in the problem tab now that the problem is solved
        # self.problem_tab_content_widget.setDisabled(False)
        # as this is the end of the callback, we do not need to process events
        # manually (since the main loop will do that for us)

        # TODO: add an exception handler to automatically re-enable the UI if
        # something goes wrong in the callback (since pyside6 already makes
        # exceptions non-fatal)
