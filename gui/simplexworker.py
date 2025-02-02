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
        self.cancelled = False

    def cancel_soon(self):
        self.cancelled = True

    @Slot()
    def run(self):
        try:
            pivot_count = 0
            try:
                while not self.cancelled:
                    self.tableau.pivot()
                    pivot_count += 1
                    # This turns out to have a race condition: if the GUI is
                    # quit the C++ representation of the SimplexWorkerSignals
                    # object that Qt uses may get deleted before cancellation
                    # is checked for.  This causes a RuntimeError to be raised.
                    # So far, I have only run into this once.
                    # Once the RuntimeError is raised, it gets caught by the
                    # outer try-except block.  As part of this, an error
                    # signal is emitted with details about the error.  However,
                    # this then causes a second RuntimeError to occur for the
                    # same reason.
                    # Since the outer try-except block has a finally block
                    # attached to it, further code runs even though an error
                    # occurs in the except block.  Because the finally block
                    # also emits a signal (to inform the main thread that the
                    # algorithm has terminated and the problem region can be
                    # re-enabled, even if the algorithm crashed for some
                    # reason) a third RuntimeError gets raised.  The thread
                    # then crashes.  This does not get picked up as a crash by
                    # my shell or vscode (both of which display an icon if a
                    # comand had a non-zero return code) since it is a crash
                    # in the thread rather than in the main program.
                    self.signals.progress.emit(pivot_count)
            except SimplexAlgorithmDoneException:
                pass
            if self.cancelled:
                self.signals.finished.emit()
                return
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
