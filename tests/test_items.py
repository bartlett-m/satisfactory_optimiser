import unittest
from satisfactoryobjects import items
from utils.suppressalllogs import SuppressAll


class TestItem(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        super(TestItem, self).setUp(
            *args,
            **kwargs
        )
        # disable logging for the module under test
        self.__log_filter_obj = SuppressAll()
        items.toplevel_logger.addFilter(self.__log_filter_obj)

    def tearDown(self, *args, **kwargs):
        super(TestItem, self).tearDown(
            *args,
            **kwargs
        )
        # re-enable logging for the module under test
        items.toplevel_logger.removeFilter(self.__log_filter_obj)

    def test_item_energy_value_not_compensated_for(self):
        # See comment on test_fluid_energy_value_compensated_for()
        # This test checks that the unit compensation is NOT applied for
        # non-fluid items.
        item_under_test = items.Item(
            "Desc_some_internal_id_for_non_fluid_item_under_test_C",
            "Some user facing name for a test item that is not a fluid",
            1,
            False
        )
        self.assertEqual(
            item_under_test.energy_value,
            1
        )

    def test_fluid_energy_value_compensated_for(self):
        # The internal units for fluids are cubic decimetres, but the units
        # displayed to the player are cubic metres.  This program should use
        # the units displayed to the player, and therefore has to convert the
        # energy values in docs.json to align with these units.
        item_under_test = items.Item(
            "Desc_some_internal_id_for_fluid_item_under_test_C",
            "Some user facing name for a test item that is a fluid",
            1,
            True
        )
        self.assertEqual(
            item_under_test.energy_value,
            1000
        )
