from PySide6.QtWidgets import QWidget, QProgressBar, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


# Would have been a subclass of QDialog but we don't want the QDialog
# behaviour of triggering a cancel on escape.  This is because this window
# will represent progress in a long-running task and so a cancellation should
# be made difficult to perform accidentally.

# This is a QWidget since we do not want the QDialog default behaviour,
# QMainWindow is designed for the main window (i.e. not a second window), and
# QWindow is intended for direct use with OpenGL or similar patterns when it
# is not used internally.
class CustomProgressDialog(QWidget):
    def __init__(self, external_cancellation_callback, *args, **kwargs):
        super(CustomProgressDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('Satisfactory Optimiser')

        layout = QVBoxLayout()

        layout.addWidget(QLabel('Running optimisation'))
        layout.addStretch(1)
        self.progress_label = QLabel()
        # the text in the progress label will get set later so dont bother
        # setting it yet anymore
        layout.addWidget(self.progress_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.cancel_button_callback)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

        # used to tell the difference between closes initiated by the main
        # application and closes initiated by the user
        self.application_is_closing_flag = False
        # called by the cancel button callback
        self.external_cancellation_callback = external_cancellation_callback

    def set_pivots(self, n_pivots: int) -> None:
        partial_str: str = None
        if n_pivots == 1:
            partial_str = '1 pivot'
        elif n_pivots == 0:
            partial_str = 'No pivots'
        else:
            partial_str = f'{n_pivots} pivots'
        self.progress_label.setText(
            partial_str + ' completed.'
        )

    def reset_and_show(self):
        self.set_pivots(0)
        self.show()

    def cleanup_on_application_close(self):
        self.application_is_closing_flag = True
        self.close()

    def closeEvent(self, event):
        if self.application_is_closing_flag:
            return super().closeEvent(event)
        else:
            # prevent the user from closing this (they should instead click
            # cancel)
            event.ignore()

    def cancel_button_callback(self):
        self.external_cancellation_callback()
