import logging
from .items import Item

toplevel_logger = logging.getLogger(__name__)

items: dict[str, Item] = dict()


def handler(obj):
    _debug_temp = False
    for _class in obj["Classes"]:
        if not _debug_temp:
            _debug_temp = True
            toplevel_logger.debug(_class)
        items[_class["ClassName"]] = Item(
            _class["ClassName"],
            _class["mDisplayName"],
            float(_class['mEnergyValue']),
            is_fluid=(_class["mForm"] in ["RF_LIQUID", "RF_GAS"])
        )
        toplevel_logger.debug(_class["ClassName"])
        toplevel_logger.debug(_class["mDisplayName"])
