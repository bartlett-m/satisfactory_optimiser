import logging

from PySide6.QtWidgets import QTabWidget, QMainWindow, QApplication
from PySide6.QtCore import QThreadPool, QSettings

from satisfactoryobjects.itemvariabletype import (
    ItemVariableType,
    ItemVariableTypes
)
# CAUTION: these better have been populated by the time Target.__init__()
# starts getting called or it will likely break
from satisfactoryobjects.recipehandler import recipes

from utils.directionenums import Direction
from utils.variabletypetags import VariableType

from .recipeusage import RecipeUsage
from .simplexworker import SimplexWorker
from .settingstabcontent import SettingsTabContent
from .solutiontabcontent import SolutionTabContent
from .problemtabcontent import ProblemTabContent


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

        self.problem_tab_content_widget = ProblemTabContent(
            main_window_reference=self
        )
        self.solution_tab_content_widget = SolutionTabContent()

        # add the tabs
        self.tabs.addTab(self.problem_tab_content_widget, 'Problem')
        self.tabs.addTab(self.solution_tab_content_widget, 'Solution')
        self.tabs.addTab(
            SettingsTabContent(
                self.settings,
                failed_notification_backend_imports
            ),
            'Settings'
        )

        # set the tab layout as the main widget
        self.setCentralWidget(self.tabs)

        self.simplex_worker_thread: SimplexWorker = None

        self.thread_pool = QThreadPool()
        MainWindow.logger.info(
            'Multithreading with a maximum of '
            f'{self.thread_pool.maxThreadCount()}'
            ' threads.'
        )

    def closeEvent(self, event):
        if self.simplex_worker_thread is not None:
            self.simplex_worker_thread.cancel_soon()
        return super().closeEvent(event)

    def process_simplex_progress(self, progress: int):
        print(f'Have completed {progress} pivots')

    def process_simplex_terminate(self):
        # TODO: have a flag that is set when closeEvent is fired,
        # and dont send the notification if it got set.
        self.simplex_worker_thread = None
        self.problem_tab_content_widget.setDisabled(False)
        notification_senders[
            self.settings.value('notifications/backend')
        ](
            'Optimisation complete', 'View the results in the Solution tab'
        )

    def process_simplex_result(self, result: list):
        # TODO: this could easily go into the solution tab content widget file
        total_power_usage = float()
        for var_id, var_val in result:
            if var_id.type == VariableType.NORMAL:
                # check for string type
                # source: https://stackoverflow.com/a/4843178
                # [accessed 2025-01-06 at 13:12]
                if isinstance(var_id.name, str) and var_val != 0:
                    self.solution_tab_content_widget.add_recipe_usage_widget_to_detail_view_layout(
                        RecipeUsage(var_id.name, var_val)
                    )
                    print(f'{var_id.name}: {var_val}')
                    total_power_usage += (
                        var_val * recipes[var_id.name].calc_power_flow_rate(
                            positive_direction=Direction.IN
                        )
                    )
                # also get the outputs
                elif isinstance(var_id.name, ItemVariableType):
                    if var_id.name.type is ItemVariableTypes.OUTPUT:
                        self.solution_tab_content_widget.add_requested_item_production_view_entry(
                            var_id.name.item,
                            var_val
                        )
            elif var_id.type == VariableType.OBJECTIVE:
                self.solution_tab_content_widget.set_objective_variable_value(var_val)
        self.solution_tab_content_widget.set_total_power_consumption(total_power_usage)
