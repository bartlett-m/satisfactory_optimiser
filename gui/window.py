# from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTabWidget, QMainWindow, QWidget, QLabel, \
    QScrollArea, QVBoxLayout, QFormLayout, QPushButton
# TODO: prepend a . to the first item after finished testing
from item import Item


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Satisfactory Optimiser")

        self.tabs = QTabWidget()

        self.problem_layout = QFormLayout()
        self.solution_layout = QVBoxLayout()

        self.problem_layout.addRow('Targets', QPushButton("Add"))

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


# testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
