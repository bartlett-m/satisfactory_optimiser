"""Enums to represent direction"""

from enum import IntFlag


class Direction(IntFlag):
    IN = 1
    OUT = 2
    BIDIRECTIONAL = 3
