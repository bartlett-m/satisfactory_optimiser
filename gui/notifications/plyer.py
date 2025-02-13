from plyer.facades import Notification
from .notificationurgency import NotificationUrgency

_facade = Notification()


def simple_add_notification(
    summary: str,
    body: str = '',
    urgency: NotificationUrgency = NotificationUrgency.NORMAL,
    id_to_replace: int = 0
) -> int:
    # Plyer does not support notification overwrite and its dbus hits api is
    # not well documented, as well as being Linux-specific
    _facade.notify(summary, body)

    return 0
