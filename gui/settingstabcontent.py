import sys
import logging

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QScrollArea,
    QMessageBox,
    QPushButton,
    QRadioButton
)

toplevel_logger = logging.getLogger(__name__)


class SettingsTabContent(QWidget):
    def __init__(
        self,
        settings_reference: QSettings,
        failed_notification_backend_imports: set[str],
        *args,
        **kwargs
    ):
        super(SettingsTabContent, self).__init__(*args, **kwargs)

        self.settings = settings_reference

        # holds the scroll area and the apply/revert buttons
        layout = QVBoxLayout()

        # make the settings scrollable (for future-proofing)
        form_container = QScrollArea()

        # widget to contain the settings FormLayout
        form_layout_container = QFrame()

        form_layout = QFormLayout()

        # layout for the notification backend radio buttons
        notification_backend_select_layout = QHBoxLayout()

        # validate and optionally repair the notification backend button
        # setting
        if self.settings.value('notifications/backend') is None:
            toplevel_logger.debug('Creating setting for notification backend')
            self.settings.setValue('notifications/backend', 'null')

        if self.settings.value('notifications/backend') in failed_notification_backend_imports:
            toplevel_logger.critical(
                'User-configured notification backend with id '
                f'{self.settings.value("notifications.backend")}'
                ' failed to load!  Warning user.'
            )
            error_dialog = QMessageBox(
                QMessageBox.Icon.Critical,
                'Configuration problem',
                'The selected notification backend failed to load.  Restore '
                'default setting for notifications and continue, or quit '
                'program for troubleshooting?',
                QMessageBox.StandardButton.RestoreDefaults | QMessageBox.StandardButton.Abort
            )
            response = error_dialog.exec()
            if response == QMessageBox.StandardButton.RestoreDefaults:
                toplevel_logger.warning(
                    'Repairing configuration: resetting notifications/backend '
                    'to null'
                )
                self.settings.setValue('notifications/backend', 'null')
            else:
                toplevel_logger.critical('User declined configuration repair.')
                toplevel_logger.critical('Exiting due to configuration error')
                sys.exit(78)

        # define the radio buttons for the notification backend
        self.notification_backend_buttons = {
            'null': (QRadioButton('None'), 'Do not send notifications'),
            'dbus': (
                QRadioButton('D-Bus'),
                'Used on Un*x and Un*x-like systems'
            ),
            'plyer': (
                QRadioButton('Plyer'),
                'Cross-platform but doesnt support some features.  Consider '
                'using a platform-specific backend if one is available.'
            )
        }

        for button_setting_id, button_tuple in self.notification_backend_buttons.items():
            button_tuple[0].setToolTip(button_tuple[1])
            if button_setting_id in failed_notification_backend_imports:
                button_tuple[0].setDisabled(True)

        # TODO: make self.notification_backend_buttons an OrderedDict or
        # something so this can be in a loop
        notification_backend_select_layout.addWidget(
            self.notification_backend_buttons['null'][0]
        )
        notification_backend_select_layout.addWidget(
            self.notification_backend_buttons['dbus'][0]
        )
        notification_backend_select_layout.addWidget(
            self.notification_backend_buttons['plyer'][0]
        )

        form_layout.addRow('Notification backend:', notification_backend_select_layout)

        form_layout_container.setLayout(form_layout)

        form_container.setWidget(form_layout_container)

        layout.addWidget(form_container)

        # apply/cancel buttons
        apply_button = QPushButton('Apply')
        apply_button.setToolTip(
            'Apply new settings to program and write to file on disk'
        )
        apply_button.clicked.connect(self.write_settings)
        cancel_button = QPushButton('Cancel')
        cancel_button.setToolTip(
            'Discard changes made to settings and reload from file on disk'
        )
        cancel_button.clicked.connect(self.reload_settings)
        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # load in the settings from the file
        self.reload_settings()

    def reload_settings(self):
        for button_setting_id, button_tuple in self.notification_backend_buttons.items():
            button_tuple[0].setChecked(
                button_setting_id == self.settings.value(
                    'notifications/backend'
                )
            )

    def write_settings(self):
        for button_setting_id, button_tuple in self.notification_backend_buttons.items():
            if button_tuple[0].isChecked():
                self.settings.setValue(
                    'notifications/backend',
                    button_setting_id
                )
