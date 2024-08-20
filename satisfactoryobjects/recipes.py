import logging
from dataclasses import dataclass
from .basesatisfactoryobject import BaseSatisfactoryObject
from .items import Item
from .itemhandler import items
from .machines import Machine, FixedPowerMachine
from .machinehandler import machines
from .nativeclasses import denamespace_satisfactory_classname
from .lookuperrors import MachineLookupError, ItemLookupError
from utils.directionenums import Direction

toplevel_logger = logging.getLogger(__name__)


@dataclass
class RecipeResource:
    item: Item
    amount: int


@dataclass
class RecipeResourceFlowData:
    item: Item
    amount: float


class Recipe(BaseSatisfactoryObject):
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str,
        dependencies: list[RecipeResource],
        products: list[RecipeResource],
        machines: list[Machine],
        time_: float,
        average_power_consumption: float = 0.0
    ) -> None:
        super().__init__(internal_class_identifier, user_facing_name)
        self.dependencies = dependencies
        self.products = products
        self.machines = machines
        self.time_ = time_
        # CAUTION: THIS IS JUNK WHEN NOT IN A VARIABLE POWER MACHINE
        # HENCE WHY ITS PRIVATE.
        # USE THE calcPowerFlowRate() FUNCTION INSTEAD
        self.__average_power_consumption = average_power_consumption

    def __str__(self) -> str:
        return (
            "Recipe:\n"
            f"{self.internal_class_identifier}\n"
            "-----\n"
            f"Known as: {self.user_facing_name}\n"
            f"Takes {self.time_} seconds per craft"
        )

    def __repr__(self) -> str:
        return (
            f"{self.internal_class_identifier}:"
            "{user_facing_name:"
            f"{self.user_facing_name},time_:{self.time_}"
            "}"
        )

    def calcResourceFlowRate(
        self,
        period: float = 60,
        calculated_direction: Direction = Direction.BIDIRECTIONAL,
        positive_direction: Direction = Direction.OUT
    ):
        if positive_direction == Direction.BIDIRECTIONAL:
            raise ValueError(
                "Only one direction may be considered a positive resource flow"
            )
        _ret: list[RecipeResourceFlowData] = list()
        crafts_per_period = period / self.time_
        if calculated_direction & Direction.IN:
            for dependency in self.dependencies:
                _ret.append(
                    RecipeResourceFlowData(
                        dependency.item,
                        dependency.amount * crafts_per_period * (
                            1
                            if positive_direction == Direction.IN
                            else -1
                        )
                    )
                )
        if calculated_direction & Direction.OUT:
            for product in self.products:
                _ret.append(
                    RecipeResourceFlowData(
                        product.item,
                        product.amount * crafts_per_period * (
                            -1
                            if positive_direction == Direction.IN
                            else 1
                        )
                    )
                )
        return _ret

    def calcPowerFlowRate(
        self,
        positive_direction: Direction = Direction.OUT,
        # every recipe seems to only have 1 registered machine
        # (presumably not the workbench)
        machine_index: int = 0
    ) -> float:
        # time not used since power flow is measured in megawatts in this game
        if positive_direction == Direction.BIDIRECTIONAL:
            raise ValueError(
                "Only one direction may be considered a positive power flow"
            )
        used_machine = self.machines[machine_index]
        if type(used_machine) is FixedPowerMachine:
            return used_machine.power_flow_rate * (
                -1
                if positive_direction == Direction.IN
                else 1
            )
        else:
            return self.__average_power_consumption * (
                -1
                if positive_direction == Direction.IN
                else 1
            )

    def parseResources(
        unparsed_resources: str,
        recipe_name: str = "[UNKNOWN]"
    ) -> list[RecipeResource]:
        # recipe_name is only used in logs to help with debugging
        result = list()
        for unparsed_resource in (unparsed_resources
                                  # strip enclosing brackets of resource
                                  # array, as well as first bracket of first
                                  # resource and last bracket of last resource
                                  [2:-2]
                                  # split into a list of resources and
                                  # strip remaining brackets
                                  .split("),(")
                                  ):
            unparsed_class, unparsed_amount = unparsed_resource.split(",")
            # no need to remove the ItemClass= manually since it will be
            # truncated during denamespacing anyway
            parsed_class = denamespace_satisfactory_classname(unparsed_class)
            # attempt to look up the item
            try:
                item = items[parsed_class]
            except KeyError:
                # item not found
                toplevel_logger.error(
                    f"Resource {parsed_class} "
                    f"of recipe {recipe_name} "
                    "not registered!"
                )
                raise ItemLookupError("Recipe references nonexistent item!")
            # remove the Amount= and convert to integer
            # TODO: check the list of items to see if it is a fluid if any
            # special handling is then needed for this
            parsed_amount = int(unparsed_amount[7:])
            result.append(
                RecipeResource(
                    item,
                    parsed_amount
                )
            )
        return result

    def parseProducedIn(
        unparsed_produced_in: str,
        recipe_name: str = "[UNKNOWN]"
    ) -> list[Machine]:
        # again, recipe_name is only used in logs
        # list here because of course theres multiple machines that can make
        # recipes (like the workbench, actually it makes logical sense now)
        result = list()
        for unparsed_machine in (unparsed_produced_in
                                 # strip enclosing brackets of machine array
                                 # as well as leading quote on first machine
                                 # and trailing quote on last machine
                                 [2:-2]
                                 # split into a list of machines and strip
                                 # remaining quotes
                                 .split('","')
                                 ):
            parsed_class = denamespace_satisfactory_classname(
                unparsed_machine
            )
            try:
                result.append(machines[parsed_class])
            except KeyError:
                # dont stop here so other machines can also be parsed
                toplevel_logger.error(
                    f"Machine {parsed_class} "
                    f"used to make recipe {recipe_name} "
                    "not registered!"
                )
        if len(result) == 0:
            raise MachineLookupError(
                "Recipe does not reference any existing machine!"
            )
        return result
