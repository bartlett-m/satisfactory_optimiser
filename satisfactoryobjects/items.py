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
    ):
        super().__init__(internal_class_identifier, user_facing_name)
        # if is_fluid then energy value mEnergyValue probably needs different
        # handling
        self.energy_value = energy_value
        self.is_fluid = is_fluid

        # TODO: implement anything else needed
