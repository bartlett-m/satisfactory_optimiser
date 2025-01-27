from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea


class ProblemTabContent(QWidget):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(ProblemTabContent, self).__init__(*args, **kwargs)

        # Holds the scroll area and the run optimisation button
        layout = QVBoxLayout()

        # Holds the form, so it is scrollable
        form_container = QScrollArea()

        # allow the form to dynamically resize as items are added and removed,
        # rather than squashing new items
        form_container.setWidgetResizable(True)

