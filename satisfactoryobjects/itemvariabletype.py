"""Class to represent whether an item variable in the linear programming
problem is the manual input from the GUI or the total including production
from machines
"""
from .items import Item


class ItemVariableType():
    def __init__(self, item: Item, is_manual_input: bool = False):
        self.item = item
        self.is_manual_input = is_manual_input

    def __eq__(self, other: object) -> bool:
        if issubclass(type(other), ItemVariableType):
            return (
                self.item.__eq__(other.item)
                and
                self.is_manual_input == other.is_manual_input
            )
        return False

    def __hash__(self) -> int:
        # this implementation of __hash__(self) was written using the help of
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # [accessed 2024-12-30 at 13:02]
        return (
            self.item.__hash__()
            ^
            self.is_manual_input.__hash__()
        )

    # temp
    # does not provide full info, but still useful for debugging
    def __repr__(self) -> str:
        return self.item.__repr__()
