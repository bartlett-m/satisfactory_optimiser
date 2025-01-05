"""Class to represent whether an item variable in the linear programming
problem is the manual input from the GUI or the total including production
from machines or the amount available to be output (total minus what is used
in recipes), and an enum to define these different possibilities.
"""
from enum import IntEnum
from .items import Item


class ItemVariableTypes(IntEnum):
    TOTAL = 0
    MANUAL_INPUT = 1
    OUTPUT = 2


class ItemVariableType():
    def __init__(self, item: Item, type: ItemVariableTypes = ItemVariableTypes.TOTAL):
        self.item = item
        self.type = type

    def __eq__(self, other: object) -> bool:
        if issubclass(type(other), ItemVariableType):
            return (
                self.item.__eq__(other.item)
                and
                self.type == other.type
            )
        return False

    def __hash__(self) -> int:
        # this implementation of __hash__(self) was written using the help of
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # [accessed 2024-12-30 at 13:02]
        return (
            self.item.__hash__()
            ^
            self.type.__hash__()
        )

    # temp
    # does not provide full info, but still useful for debugging
    def __repr__(self) -> str:
        return self.item.__repr__()
