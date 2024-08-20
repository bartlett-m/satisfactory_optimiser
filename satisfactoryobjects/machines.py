import logging
from .basesatisfactoryobject import BaseSatisfactoryObject

toplevel_logger = logging.getLogger(__name__)


class Machine(BaseSatisfactoryObject):
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str,
    ):
        super().__init__(internal_class_identifier, user_facing_name)
        # power flow rates on variable power machines are defined as the
        # minimum for the recipe with the lowest minimum and the maximum for
        # the recipe with the highest maximum, so are not actually useful for
        # determining consumption.  power consumption is only usefully defined
        # in recipes for these machines.  for fixed power machines, the power
        # consumption is not usefully defined in recipes and is instead only
        # usefully defined in the machine.


class FixedPowerMachine(Machine):
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str,
        power_flow_rate: float
    ):
        super().__init__(internal_class_identifier, user_facing_name)
        self.power_flow_rate = power_flow_rate
