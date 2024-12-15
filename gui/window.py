from PySide6.QtWidgets import (
    QTabWidget,
    QMainWindow,
    QWidget,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QFormLayout,
    QPushButton
)
from .item import Item
from .targets_widget import TargetsWidget, Target


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Satisfactory Optimiser")

        self.tabs = QTabWidget()

        self.problem_layout = QFormLayout()
        self.solution_layout = QVBoxLayout()

        add_target_button = QPushButton("Add")
        add_target_button.clicked.connect(self.add_target)
        self.problem_layout.addRow('Targets', add_target_button)
        self.targets_widget = TargetsWidget()
        self.problem_layout.addRow(self.targets_widget)

        self.problem_layout.addRow('Resource Availability', QPushButton("Add"))

        self.problem_layout.addRow(QLabel("Weightings"))

        self.problem_layout.addRow(QPushButton("Run Optimisation"))

        # why does it work here, and not after solution_widget.setWidget
        # TODO: figure out above and fix
        self.solution_layout.addWidget(Item("test1", 1))
        self.solution_layout.addWidget(Item("test2", 2))
        self.solution_layout.addWidget(Item("test3", 3))

        solution_widget = QScrollArea()

        problem_layout_container = QWidget()
        problem_layout_container.setLayout(self.problem_layout)

        solution_layout_container = QWidget()
        solution_layout_container.setLayout(self.solution_layout)

        solution_widget.setWidget(solution_layout_container)

        self.tabs.addTab(problem_layout_container, "Problem")
        self.tabs.addTab(solution_widget, "Solution")
        # self.tabs.setTabEnabled(1, False)  # like this we can disable a tab

        self.setCentralWidget(self.tabs)

    def add_target(self):
        self.targets_widget.add_target(Target())
