from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSplitter, QWidget, QScrollArea

from .solutionquickoverview import SolutionQuickOverview
from .config_constants import LARGE_STRETCH_FACTOR_CONSTANT
from .recipeusage import RecipeUsage

from thirdparty.flowlayout import FlowLayout
from thirdparty.clearlayout import clear_layout


class SolutionTabContent(QSplitter):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(SolutionTabContent, self).__init__(*args, **kwargs)

        self.setOrientation(Qt.Orientation.Vertical)

        # According to my old comments from when this wasnt in a separate file,
        # this was required to make the scroll area work properly with the
        # flow layout.  But knowing how messy that old code was, it could well
        # have been me using the wrong variable name somewhere.  Regardless, I
        # am going to use what I know works.
        detail_view_layout_container = QWidget()

        # held within a scroll area
        self.detail_view_layout = FlowLayout(detail_view_layout_container)

        # scrollable region for the info on the individual recipes
        detail_view_container = QScrollArea()

        # put the flowlayout wrapper widget in the scrollarea
        detail_view_container.setWidget(detail_view_layout_container)

        # allow the scroll area to dynamically resize, instead of squishing
        # new items (so it can work as intended)
        detail_view_container.setWidgetResizable(True)

        self.addWidget(detail_view_container)

        # widget for a quick overview of the solution
        self.quick_view_widget = SolutionQuickOverview()

        self.addWidget(self.quick_view_widget)

        # make the solution quick overview be the smaller one by default
        self.setStretchFactor(
            # act on first widget i.e. the solution details
            0,
            # some large constant i.e. make this take up a lot of space, in
            # practice this is however much is available
            LARGE_STRETCH_FACTOR_CONSTANT
        )

        # do not permit the detailed solution view to be hidden
        self.setCollapsible(0, False)

        # passthrough some functions
        self.add_requested_item_production_view_entry = self.quick_view_widget.add_requested_item_production_view_entry
        self.set_objective_variable_value = self.quick_view_widget.set_objective_variable_value
        self.set_total_power_consumption = self.quick_view_widget.set_total_power_consumption
        self.add_recipe_usage_widget_to_detail_view_layout = self.detail_view_layout.addWidget

    def reset_all(self):
        clear_layout(self.detail_view_layout)
        self.quick_view_widget.reset_all()
