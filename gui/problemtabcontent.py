import logging
from fractions import Fraction
# prevent circular import at runtime but still allow for MainWindow type hint
# static type checkers interpret this constant as True, but it is False at
# runtime
# source: https://medium.com/@k.a.fedorov/type-annotations-and-circular-imports-0a8014cd243b
# [accessed 2025-01-31 at 09:21]
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QScrollArea,
    QSizePolicy,
    QDoubleSpinBox
)

from .config_constants import SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS
from .constraints_widget import ConstraintsWidget, Constraint
from .simplexworker import SimplexWorker

if TYPE_CHECKING:
    # only used for type hint, so does not need to be imported at runtime
    # (and if it is, the code crashes due to a circular import)
    from .window import MainWindow

from optimisationsolver.simplex import Inequality, ObjectiveEquation, Variable


from utils.directionenums import Direction
# from utils.variabletypetags import VariableType

from satisfactoryobjects.items import Item
from satisfactoryobjects.itemvariabletype import (
    ItemVariableType,
    ItemVariableTypes
)
from satisfactoryobjects.lookuperrors import RecipeLookupError
from satisfactoryobjects.resourceduplicatetypingsaver import resource_duplicate_typing_saver
# CAUTION: these better have been populated already, or things will definitely
# break
from satisfactoryobjects.itemhandler import items
from satisfactoryobjects.recipelookup import lookup_recipes


toplevel_logger = logging.getLogger(__name__)


def make_form_subsection_header(
    subsection_label: str,
    button_label: str = 'Add'
) -> tuple[QHBoxLayout, QPushButton]:
    '''Helper function to make the subsection header for a form'''
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


class ProblemTabContent(QWidget):
    logger = toplevel_logger.getChild('ProblemTabContent')

    def __init__(
        self,
        # the type hint for this is implemented as a forward reference since
        # otherwise it will be undefined at runtime (as MainWindow is only
        # imported when a static type checker is running due to the circular
        # import dependency)
        # source: https://peps.python.org/pep-0484/#forward-references
        # [accessed 2025-01-31 at 09:16]
        # second source:
        # https://medium.com/@k.a.fedorov/type-annotations-and-circular-imports-0a8014cd243b
        # [accessed 2025-01-31 at 09:21]
        main_window_reference: 'MainWindow',
        *args,
        **kwargs
    ):
        super(ProblemTabContent, self).__init__(*args, **kwargs)

        # so the callbacks can access it
        self.main_window_reference = main_window_reference

        # Holds the scroll area and the run optimisation button
        layout = QVBoxLayout()

        # Holds the form frame, so it is scrollable
        form_container = QScrollArea()

        # allow the form to dynamically resize as items are added and removed,
        # rather than squashing new items
        form_container.setWidgetResizable(True)

        # Holds the layout used by the form.
        form_layout_container = QFrame()

        # At one point this was an actual QFormLayout, but I found that it was
        # easier to get the responsive design behaviour that I wanted by using
        # a QVBoxLayout as the outermost layout for the form.
        form_layout = QVBoxLayout(form_layout_container)

        # Production targets section

        # custom widget for production targets
        self.targets_widget = ConstraintsWidget()
        # start off with one target
        self.targets_widget.add_constraint(Constraint(items, default_value=1))
        # header for the production targets section
        (
            targets_section_header,
            add_target_button
        ) = make_form_subsection_header(
            'Target weightings'
        )

        # setup the callback to add new targets
        add_target_button.clicked.connect(self.add_target)
        # add the section header
        form_layout.addLayout(targets_section_header)
        # add the section content
        form_layout.addWidget(self.targets_widget)

        # Resource availability constraints section
        self.resource_availability_constraints_widget = ConstraintsWidget()
        # Start with one resource availability constraint per basic resource.
        # First, add the solid resources that are present in all versions of
        # the docs file (iron, caterium, copper, limestone, coal, quartz,
        # sulphur, uranium, bauxite).
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
            # As mentioned before, these resources are present in all versions
            # of the docs file that one would be likely to use (i.e. both
            # update 8 and release 1.0) and thus require no special checks for
            # presence, so don't bother with the dictionary lookup.
            # Although a user might have persisted a game installation from an
            # update before one of these resources was introduced, they are
            # likely not using external planners anyway due to lack of support
            # (i.e. I am providing game version support parity with popular
            # planners as of writing this) and I did not start playing
            # Satisfactory before update 8 was released (or maybe it was
            # update 7?  either way I don't have a copy of the docs file to
            # test with)
            self.resource_availability_constraints_widget.add_constraint(
                Constraint(items, resource)
            )
        # final ore node: SAM - this was not present in the update 8 docs file
        # and thus its existence must be first verified.
        # (this also can double as a heuristic for whether the docs file
        # provided was from the early access period i.e. before release 1.0)
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
            # in these versions SAM ore existed but had no use and couldnt be
            # automated - miners would stop extracting after ~50 ore had been
            # extracted and would not restart until the game was reloaded.

            # see above - SAM ore doesnt exist in this version of the file and
            # is not relevant to production in the corresponding version of
            # the game.
            pass
        # Now that all the solid resources have been added, add the liquid
        # resources.  Although quite a few fluids were added for version 1.0
        # of the game, none of them are basic resources (my definition of
        # basic resource = has a corresponding node type or production
        # location is otherwise constrained, and this form of production is
        # not implemented as a recipe i.e. that one fluid with a zero-cost
        # recipe that version 1.0 added doesnt count as a basic resource since
        # you can place its production machine anywhere and it is technically
        # a recipe, but water is a basic resource since you can only put water
        # extractors in whatever the game considers to be deep enough water,
        # or get it from a resource well)
        for resource in resource_duplicate_typing_saver(
            [
                "Water",
                "LiquidOil",  # Crude oil
                "NitrogenGas"
            ]
        ):
            # Again, these resources are present in all versions of the docs
            # file that I have access to (and the only reason that I could see
            # for keeping an install from before update 8 would be for
            # speedrunning, and even then update 8 has its fair share of
            # speedrun glitches that one might keep an install for - now that
            # modding support has caught up to release 1.0 I can't see casual
            # players remaining on update 8 unless they really don't want to
            # fix anything that depends on the few late-game recipes that have
            # changed, and if a speedrunner was running an older version the
            # routing would likely be done manually and since update 8 had a
            # glitch (patched not due to its main effect of allowing infinite
            # production of literally anything with a defined recipe but due
            # to its side effect of sometimes crashing the game) that could
            # allow any machine to produce any recipe at max clock speed, at
            # the equivalent power consumption of min clock speed, and with no
            # resource consumption, such a planner is irrelevant to begin with)
            self.resource_availability_constraints_widget.add_constraint(
                Constraint(items, resource)
            )

        # create the header for the resource availability section
        (
            resource_availability_section_header,
            add_resource_availability_constraint_button
        ) = make_form_subsection_header(
            'Resource Availability'
        )
        # setup the callback to add new constraints
        add_resource_availability_constraint_button.clicked.connect(
            self.add_resource_availability_constraint
        )
        # add the section header
        form_layout.addLayout(
            resource_availability_section_header
        )
        # add the section content
        form_layout.addWidget(
            self.resource_availability_constraints_widget
        )

        # header for the weightings widget has no add button
        # since there are few weightings
        form_layout.addWidget(QLabel('Weightings'))
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

        self.weightings_form.addRow('Power usage', self.power_usage_spin_box)

        # possible FIXME: maybe encapsulate the QFormLayout in a QWidget to
        # get a more consistent look with the margins
        form_layout.addLayout(self.weightings_form)

        # put the layout container widget in the scroll area
        form_container.setWidget(form_layout_container)

        # add the scroll area to the tab layout
        layout.addWidget(form_container)
        # create the run button
        run_optimisation_button = QPushButton('Run Optimisation')
        # and connect the clicked signal to the appropriate slot
        run_optimisation_button.clicked.connect(self.run_optimisation)
        # Add the run button outside the scroll area but within the tab layout,
        # so it is always visible without any scrolling required.
        layout.addWidget(run_optimisation_button)

        # Now, set this widget's layout.
        self.setLayout(layout)

    def add_target(self):
        '''Adds a new production target to the production targets widget'''
        self.targets_widget.add_constraint(Constraint(items, default_value=1))

    def add_resource_availability_constraint(self):
        '''Adds a new resource availability constraint to the resource availability constraints widget'''
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items)
        )

    def run_optimisation(self):
        # disable this widget (to prevent settings from being overridden as
        # they are being read)
        self.setDisabled(True)
        # disabling a widget implicitly disables all its children, and
        # enabling a widget implicitly enables all its children that have not
        # been explicitly disabled, so there is no need to worry about the
        # remove constraint buttons being enabled when they shouldnt be
        # reference for this is https://stackoverflow.com/a/34892529
        # [accessed 2025-01-05 at 13:45]
        # note that it specifically talks about the c++ version of qt5, but it
        # seems to still apply to qt6 (and thus its language bindings)

        # process events (so that the UI disable event is handled)
        self.main_window_reference.qt_application_reference.processEvents()

        # clear anything left over in the solution tab from previous runs
        self.main_window_reference.solution_tab_content_widget.reset_all()
        # make sure that this gets processed
        # FIXME: this doesnt actually work - the deletion only gets processed
        # after the callback is done?
        # apparently this is due to DeferredDelete events only being processed
        # in the main event loop.  see
        # https://doc.qt.io/qtforpython-6/PySide6/QtCore/QEventLoop.html
        # [accessed 2025-01-04 at 09:49]
        # for the documentation on this.
        self.main_window_reference.qt_application_reference.processEvents()

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

        manually_set_constraint_values: dict[Item, Fraction] = dict()

        # add the constraints for the input items
        for available_resource, available_resource_rate in self.resource_availability_constraints_widget.get_constraints():
            number_per_minute = available_resource_rate
            if number_per_minute == 0:
                ProblemTabContent.logger.warning(
                    'Constraint for item with id '
                    f'{available_resource}'
                    ' is set to zero!  Skipping.'
                )
            else:
                resource = items[available_resource]
                manually_set_constraints.add(resource)
                manually_set_constraint_values[resource] = Fraction(
                    number_per_minute
                )

        # add the constraints for the absolute numbers of items
        for resource in items.values():
            constraint_variables: list[Variable] = [
                Variable(
                    ItemVariableType(resource, ItemVariableTypes.TOTAL),
                    1
                )
            ]
            # if a manual input of this resource exists, add it to the constraint
            #if resource in manually_set_constraints:
            #    constraint_variables.append(Variable(ItemVariableType(resource, ItemVariableTypes.MANUAL_INPUT), -1))
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
                            constraint_variables.append(
                                Variable(
                                    recipe.internal_class_identifier,
                                    Fraction(flow_data.amount)
                                )
                            )
            except RecipeLookupError:
                ProblemTabContent.logger.debug(
                    'No recipes produce item with id '
                    f'{resource.internal_class_identifier}'
                    ', only adding data about manual input'
                )

            cons = Inequality(
                constraint_variables,
                (
                    manually_set_constraint_values[resource]
                    if resource in manually_set_constraints
                    else 0
                )
            )
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
                            constraint_variables.append(
                                Variable(
                                    recipe.internal_class_identifier,
                                    Fraction(flow_data.amount)
                                )
                            )
                if len(constraint_variables) == 1:
                    ProblemTabContent.logger.debug(
                        'No feasible recipe consumes item with id '
                        f'{resource.internal_class_identifier}'
                        ', not adding usage constraint'
                    )
                else:
                    problem_constraints.append(Inequality(constraint_variables, 0))
            except RecipeLookupError:
                ProblemTabContent.logger.debug(
                    'No recipes consume item with id '
                    f'{resource.internal_class_identifier}'
                    ', not adding usage constraint unless target'
                )
                # TODO: with regards to above about putting in the try block:
                # replace this logic with something better
                if len(constraint_variables) == 2:
                    problem_constraints.append(
                        Inequality(constraint_variables, 0)
                    )

        # add the objectives and their weights
        problem_constraints.append(ObjectiveEquation([
            Variable(ItemVariableType(items[target_weight[0]], ItemVariableTypes.OUTPUT), target_weight[1] * -1)
            for target_weight
            in target_weights
        ]))

        # print(len(problem_constraints))

        self.main_window_reference.simplex_worker_thread = SimplexWorker(problem_constraints)
        self.main_window_reference.simplex_worker_thread.signals.result.connect(
            self.main_window_reference.process_simplex_result
        )
        self.main_window_reference.simplex_worker_thread.signals.finished.connect(
            self.main_window_reference.process_simplex_terminate
        )
        self.main_window_reference.simplex_worker_thread.signals.progress.connect(
            self.main_window_reference.process_simplex_progress
        )

        self.main_window_reference.thread_pool.start(self.main_window_reference.simplex_worker_thread)

