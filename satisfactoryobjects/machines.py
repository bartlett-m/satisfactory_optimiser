import logging
from .basesatisfactoryobject import BaseSatisfactoryObject

toplevel_logger = logging.getLogger(__name__)


class Machine(BaseSatisfactoryObject):
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str,
    ) -> None:
        super().__init__(internal_class_identifier, user_facing_name)
        # power flow rates on variable power machines are defined as the
        # minimum for the recipe with the lowest minimum and the maximum for
        # the recipe with the highest maximum, so are not actually useful for
        # determining consumption.  power consumption is only usefully defined
        # in recipes for these machines.  for fixed power machines, the power
        # consumption is not usefully defined in recipes and is instead only
        # usefully defined in the machine.

    def __eq__(self, other: object) -> bool:
        return super(Machine, self).__eq__(other)

    def __hash__(self) -> int:
        # as of all commits on 2024-12-30 before 13:45, __hash__(self)
        # implementations on any file in the satisfactoryobjects module
        # (including this one) were writen using the help of
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # [accessed 2024-12-30 at 13:02]
        # (note that this impl. is just borrowing one made referencing the
        # above source but in the parent class due to nothing being changed
        # about this class)
        return super(Machine, self).__hash__()


class FixedPowerMachine(Machine):
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str,
        power_flow_rate: float
    ) -> None:
        super().__init__(internal_class_identifier, user_facing_name)
        self.power_flow_rate = power_flow_rate

    def __eq__(self, other: object) -> bool:
        if issubclass(type(other), FixedPowerMachine):
            return (
                super(FixedPowerMachine, self).__eq__(other)
                and
                self.power_flow_rate == other.power_flow_rate
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
            self.power_flow_rate.__hash__()
        )
