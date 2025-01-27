from PySide6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy

from .constraints_widget import ConstraintsWidget, Constraint

from satisfactoryobjects.resourceduplicatetypingsaver import resource_duplicate_typing_saver
# CAUTION: these better have been populated already, or things will definitely
# break
from satisfactoryobjects.itemhandler import items


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
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(ProblemTabContent, self).__init__(*args, **kwargs)

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
            targets_subsection_header,
            add_target_button
        ) = make_form_subsection_header(
            'Target weightings'
        )