'''Notification urgencies used by the backend-agnositc calls'''

from enum import IntEnum


class NotificationUrgency(IntEnum):
    LOW = 0
    NORMAL = 1
    CRITICAL = 2
