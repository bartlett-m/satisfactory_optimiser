import traceback
import sys
from enum import IntEnum

from PySide6.QtCore import QRunnable, Slot, Signal, QObject
from optimisationsolver.simplex import Tableau, Inequality, SimplexAlgorithmDoneException


class CancellationStatus(IntEnum):
    # used when the program hasn't been cancelled
    NOT_CANCELLED = 0
    # used when the algorithm is cancelled for some reason that doesnt involve
    # closing the program and thus we do not need to worry about use-after-free
    NORMAL_CANELLATION = 1
    # used when the program is exiting and thus Qt may have created a
    # use-after-free for us if we try and use signals
    ON_EXIT_CANCELLATION = 2

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
        self.cancelled = CancellationStatus.NOT_CANCELLED

    def cancel_soon(self, on_exit_cancellation: bool = False):
        self.cancelled = (
            CancellationStatus.ON_EXIT_CANCELLATION
            if on_exit_cancellation
            else CancellationStatus.NORMAL_CANELLATION
        )

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
                    if self.cancelled != CancellationStatus.ON_EXIT_CANCELLATION:
                        self.signals.progress.emit(pivot_count)
            except SimplexAlgorithmDoneException:
                pass
            if self.cancelled == CancellationStatus.NORMAL_CANELLATION:
                self.signals.finished.emit()
            if self.cancelled:
                return
            result = self.tableau.get_variable_values()
        # equivalent to bare except but doesn't trigger flake8
        except BaseException:
            traceback.print_exc()
            if self.cancelled != CancellationStatus.ON_EXIT_CANCELLATION:
                self.signals.error.emit(
                    sys.exc_info()
                )
        else:
            if not self.cancelled:
                self.signals.result.emit(result)
        finally:
            if self.cancelled != CancellationStatus.ON_EXIT_CANCELLATION:
                self.signals.finished.emit()
