"""Some utility exceptions"""


class AlgorithmDoneException(BaseException):
    """A control flow exception raised when trying to step an
    already-completed algorithm"""
    pass
