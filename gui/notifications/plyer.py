from plyer import notification
from .notificationurgency import NotificationUrgency


def simple_add_notification(
    summary: str,
    body: str = '',
    urgency: NotificationUrgency = NotificationUrgency.NORMAL,
    id_to_replace: int = 0
) -> int:
    # Plyer does not support notification overwrite and its dbus hits api is
    # not well documented, as well as being Linux-specific
    notification.notify(summary, body)

    return 0
