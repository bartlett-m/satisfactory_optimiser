"""Enums to represent the type of variable in linear programming equations"""

from enum import Enum


class VariableType(Enum):
    NORMAL = 1
    SLACK = 2
    CONSTANT = 3
    OBJECTIVE = 4
