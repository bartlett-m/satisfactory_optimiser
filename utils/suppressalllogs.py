'''Logging filter to disable all logging for use in unit tests'''
# double-underscore to prevent accidental use of this instead of SuppressAll
from logging import Filter as __Filter


class SuppressAll(__Filter):
    def __init__(self, *args, **kwargs):
        super(SuppressAll, self).__init__(*args, **kwargs)

    def filter(self, record):
        return False
