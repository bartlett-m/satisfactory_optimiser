import traceback
import sys

from PySide6.QtCore import QRunnable, Slot, Signal, QObject
from optimisationsolver.simplex import Tableau, Inequality, SimplexAlgorithmDoneException

# using code from
# https://www.pythonguis.com/tutorials/multithreading-pyside6-applications-qthreadpool/
# [accessed 2025-01-06 at 13:55]
# it has been slightly modified to spread it across multiple files and to
# better integrate it with my code, as well as to fix issues raised by flake8


class SimplexWorkerSignals(QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(list)
    progress = Signal(int)


class SimplexWorker(QRunnable):
    def __init__(self, problem: list[Inequality], *args, **kwargs):
        super(SimplexWorker, self).__init__(*args, **kwargs)
        self.tableau = Tableau(problem)
        self.signals = SimplexWorkerSignals()

    @Slot()
    def run(self):
        try:
            pivot_count = 0
            try:
                while True:
                    self.tableau.pivot()
                    pivot_count += 1
                    self.signals.progress.emit(pivot_count)
            except SimplexAlgorithmDoneException:
                pass
            result = self.tableau.get_variable_values()
        # equivalent to bare except but doesn't trigger flake8
        except BaseException:
            traceback.print_exc()
            exception_type, exception_value = sys.exc_info()[:2]
            self.signals.error.emit(
                (exception_type, exception_value, traceback.format_exc())
            )
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
