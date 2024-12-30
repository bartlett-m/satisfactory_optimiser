import unittest
from satisfactoryobjects import itemhandler, items
from utils.suppressalllogs import SuppressAll


class TestItemHandler(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        super(TestItemHandler, self).setUp(
            *args,
            **kwargs
        )
        # disable logging for the module under test
        self.__log_filter_obj = SuppressAll()
        items.toplevel_logger.addFilter(self.__log_filter_obj)

    def tearDown(self, *args, **kwargs):
        super(TestItemHandler, self).tearDown(
            *args,
            **kwargs
        )
        # clear up global state
        itemhandler.items = dict()
        # re-enable logging for the module under test
        items.toplevel_logger.removeFilter(self.__log_filter_obj)

    def test_handler(self):
        # TODO: If I add any more parts of the item that are handled, make
        # sure to add these to the test data here.
        itemhandler.handler(
            {
                "Classes": [
                    {
                        "ClassName": "Desc_ExampleTestSolidNoEnergy_C",
                        "mDisplayName": "Example test solid without energy "
                        "value",
                        "mEnergyValue": "0.000000",
                        "mForm": "RF_SOLID"
                    },
                    {
                        "ClassName": "Desc_ExampleTestSolidWithEnergy_C",
                        "mDisplayName": "Example test solid with energy value",
                        "mEnergyValue": "400.000000",
                        "mForm": "RF_SOLID"
                    },
                    {
                        "ClassName": "Desc_ExampleTestLiquidNoEnergy_C",
                        "mDisplayName": "Example test liquid without energy "
                        "value",
                        "mEnergyValue": "0.000000",
                        "mForm": "RF_LIQUID"
                    },
                    {
                        "ClassName": "Desc_ExampleTestLiquidWithEnergy_C",
                        "mDisplayName": "Example test liquid with energy "
                        "value",
                        "mEnergyValue": "0.400000",
                        "mForm": "RF_LIQUID"
                    },
                    {
                        "ClassName": "Desc_ExampleTestGasNoEnergy_C",
                        "mDisplayName": "Example test gas without energy "
                        "value",
                        "mEnergyValue": "0.000000",
                        "mForm": "RF_GAS"
                    },
                    {
                        "ClassName": "Desc_ExampleTestGasWithEnergy_C",
                        "mDisplayName": "Example test gas with energy value",
                        "mEnergyValue": "3.600000",
                        "mForm": "RF_GAS"
                    }
                ]
            }
        )
        self.assertEqual(
            itemhandler.items,
            {
                "Desc_ExampleTestSolidNoEnergy_C": items.Item(
                    "Desc_ExampleTestSolidNoEnergy_C",
                    "Example test solid without energy value",
                    float(0)
                ),
                "Desc_ExampleTestSolidWithEnergy_C": items.Item(
                    "Desc_ExampleTestSolidWithEnergy_C",
                    "Example test solid with energy value",
                    float(400)
                ),
                "Desc_ExampleTestLiquidNoEnergy_C": items.Item(
                    "Desc_ExampleTestLiquidNoEnergy_C",
                    "Example test liquid without energy value",
                    float(0),
                    True
                ),
                "Desc_ExampleTestLiquidWithEnergy_C": items.Item(
                    "Desc_ExampleTestLiquidWithEnergy_C",
                    "Example test liquid with energy value",
                    0.4,
                    True
                ),
                "Desc_ExampleTestGasNoEnergy_C": items.Item(
                    "Desc_ExampleTestGasNoEnergy_C",
                    "Example test gas without energy value",
                    float(0),
                    True
                ),
                "Desc_ExampleTestGasWithEnergy_C": items.Item(
                    "Desc_ExampleTestGasWithEnergy_C",
                    "Example test gas with energy value",
                    3.6,
                    True
                )
            }
        )
