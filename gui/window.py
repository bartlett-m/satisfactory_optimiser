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

# CAUTION: these better have been populated by the time Target.__init__()
# starts getting called or it will likely break
from satisfactoryobjects.recipehandler import recipes
from satisfactoryobjects.itemhandler import items

from .item import Item
from .constraints_widget import ConstraintsWidget, Constraint


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


class MainWindow(QMainWindow):
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
        # TODO: start with constraints for all the basic resources
        # TODO: set these with a loop
        # ore nodes
        # iron, caterium, copper, limestone, coal, quartz, sulfur, uranium,
        # bauxite, SAM
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_OreIron_C")
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_OreCopper_C")
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_Stone_C")  # Limestone
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_Coal_C")
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_OreGold_C")  # Caterium
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_Sulfur_C")
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_RawQuartz_C")
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_OreBauxite_C")
        )
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items, "Desc_OreUranium_C")
        )
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

        # put the layout container widget in the scroll area
        problem_form_container.setWidget(problem_form_layout_container)

        # add the scroll area to the tab layout
        self.problem_layout.addWidget(problem_form_container)
        run_optimisation_button = QPushButton("Run Optimisation")
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
