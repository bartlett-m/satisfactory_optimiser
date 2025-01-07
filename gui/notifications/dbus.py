from enum import Enum
import functools
import dbus
# provided by dbus-python


# note that due to limitations of dbus-python, this enum must be used as DbusNotificationUrgency.SOMETHING.value
class DbusNotificationUrgency(Enum):
    LOW = dbus.Byte(0)
    NORMAL = dbus.Byte(1)
    CRITICAL = dbus.Byte(2)


session_bus = dbus.SessionBus()

notify_portal = session_bus.get_object(
    'org.freedesktop.Notifications',
    '/org/freedesktop/Notifications'
)

_add_notification = functools.partial(
    notify_portal.get_dbus_method('Notify', 'org.freedesktop.Notifications'),
    'Satisfactory Optimiser'  # app name
)


# when called, returns the id of the notification to allow it to be overwritten
# cannot effectively use functools.partial due to the awkward order of the arguments of the original
def add_notification(summary: str, body: str = '', hints: dict = {'urgency': DbusNotificationUrgency.NORMAL.value}, timeout: int = -1, id: int = 0) -> int:
    _add_notification(
        id,  # id of notification to replace, or 0
        '',  # would be app icon
        summary,  # brief description
        body,  # detailed description or empty
        [],  # actions as array of strings - even elements from index 0 would be internal identifiers, odd elements are strings displayed to user
        hints,  # can be empty.  used to set urgency among other things
        timeout  # expire timeout.  -1 for server settings (generally dependent on urgency), 0 for never, anything above for time in ms after which the notification should be closed
    )
