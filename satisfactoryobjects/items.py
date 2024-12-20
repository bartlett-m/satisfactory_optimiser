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
        # if is_fluid then energy value mEnergyValue probably needs different
        # handling
        self.energy_value = energy_value
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
            f"Has energy value of {self.energy_value}\n"
            f"Is {("" if self.is_fluid else "not ")}a fluid"
        )
