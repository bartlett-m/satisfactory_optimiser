import logging

from .machines import Machine, FixedPowerMachine

toplevel_logger = logging.getLogger(__name__)

machines: dict[str, Machine] = dict()


def fixed_power_machine_handler(obj):
    for _class in obj["Classes"]:
        machines[_class["ClassName"]] = FixedPowerMachine(
            _class["ClassName"],
            _class["mDisplayName"],
            float(_class["mPowerConsumption"]) * -1
        )


def variable_power_machine_handler(obj):
    for _class in obj["Classes"]:
        machines[_class["ClassName"]] = Machine(
            _class["ClassName"],
            _class["mDisplayName"]
        )
