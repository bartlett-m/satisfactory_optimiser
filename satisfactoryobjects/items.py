import logging
from .basesatisfactoryobject import BaseSatisfactoryObject

toplevel_logger = logging.getLogger(__name__)


class Item(BaseSatisfactoryObject):
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str,
        energy_value,
        is_fluid=False
    ) -> None:
        super().__init__(internal_class_identifier, user_facing_name)
        # internal units for fluid volume are (dm)^3 (or 1000th of m^3)
        # whereas units displayed to the player are m^3
        # if is_fluid then energy value mEnergyValue probably needs different
        # handling
        self.energy_value = (
            energy_value * 1000  # compensate for volume units
            if is_fluid
            else energy_value
        )
        self.is_fluid = is_fluid

        # TODO: implement anything else needed

    def __repr__(self) -> str:
        return (
            f"{self.internal_class_identifier}:"
            "{user_facing_name:"
            f"{self.user_facing_name},energy_value:{self.energy_value},"
            f"is_fluid:{self.is_fluid}"
            "}"
        )

    def __str__(self) -> str:
        return (
            "Item:\n"
            f"{self.internal_class_identifier}\n"
            "-----\n"
            f"Known as: {self.user_facing_name}\n"
            f"Has energy value of {self.energy_value}MJ "
            f"{"m^-3" if self.is_fluid else "(item)^-1"}\n"
            f"Is {("" if self.is_fluid else "not ")}a fluid"
        )

    def __eq__(self, other: object) -> bool:
        if issubclass(type(other), Item):
            return (
                super(Item, self).__eq__(other)
                and self.energy_value == other.energy_value
                and self.is_fluid == other.is_fluid
            )
        return False

    def __hash__(self) -> int:
        # as of all commits on 2024-12-30 before 13:45, __hash__(self)
        # implementations on any file in the satisfactoryobjects module
        # (including this one) were writen using the help of
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # [accessed 2024-12-30 at 13:02]
        return (
            super().__hash__()
            ^
            self.energy_value.__hash__()
            ^
            self.is_fluid.__hash__()
        )
