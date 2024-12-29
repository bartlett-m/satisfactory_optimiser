import unittest
from satisfactoryobjects import nativeclasses
from utils.suppressalllogs import SuppressAll


class TestDenamespaceSatisfactoryClassname(unittest.TestCase):
    def setUp(self, *args, **kwargs):
        super(TestDenamespaceSatisfactoryClassname, self).setUp(
            *args,
            **kwargs
        )
        # disable logging for the module under test
        self.__log_filter_obj = SuppressAll()
        nativeclasses.toplevel_logger.addFilter(self.__log_filter_obj)

    def tearDown(self, *args, **kwargs):
        super(TestDenamespaceSatisfactoryClassname, self).tearDown(
            *args,
            **kwargs
        )
        # re-enable logging for the module under test
        nativeclasses.toplevel_logger.removeFilter(self.__log_filter_obj)

    def test_pipeline_pump_mk2_capitalisation_edge_case(self):
        """
        This particular class name had differing capitalisation, which fell
        afoul of a since-removed check.
        """
        self.assertEqual(
            nativeclasses.denamespace_satisfactory_classname(
                "ItemClass=/Script/Engine.BlueprintGeneratedClass'\"/Game/"
                "FactoryGame/Buildable/Factory/PipePumpMk2/"
                "Desc_PipelinePumpMK2.Desc_PipelinePumpMk2_C\"'"
            ),
            "Desc_PipelinePumpMk2_C"
        )

    def test_corrupted_classname_no_dot_errors(self):
        # fictional classname that removes the stripped-off section and then
        # has a corrupted classname that should result in an error
        with self.assertRaises(ValueError):
            nativeclasses.denamespace_satisfactory_classname(
                "/missing_dot_and_a_repeat\"'"
            )

    def test_corrupted_classname_two_dots_errors(self):
        # fictional classname that removes the stripped-off section and then
        # has a corrupted classname that should result in an error
        with self.assertRaises(ValueError):
            nativeclasses.denamespace_satisfactory_classname(
                "/two_dots_and_a_repeat..two_dots_and_a_repeat\"'"
            )

    def test_corrupted_classname_three_dots_errors(self):
        # fictional classname that removes the stripped-off section and then
        # has a corrupted classname that should result in an error
        with self.assertRaises(ValueError):
            nativeclasses.denamespace_satisfactory_classname(
                "/three_dots.and_a_repeat.three_dots.and_a_repeat\"'"
            )

    def test_with_normal_parameters(self):
        # some pre update 8 classname that is formatted the same way as most
        # of the classnames
        self.assertEqual(
            nativeclasses.denamespace_satisfactory_classname(
                "ItemClass=/Script/Engine.BlueprintGeneratedClass'\"/Game/"
                "FactoryGame/Resource/Parts/IronIngot/Desc_IronIngot."
                "Desc_IronIngot_C\"'"
            ),
            "Desc_IronIngot_C"
        )

    def test_with_release_one_point_zero_parameters(self):
        # the order of the quote types was reversed in the release 1.0
        # docs.json for whatever reason
        self.assertEqual(
            nativeclasses.denamespace_satisfactory_classname(
                "ItemClass=\"/Script/Engine.BlueprintGeneratedClass'/Game/"
                "FactoryGame/Resource/Parts/IronIngot/Desc_IronIngot."
                "Desc_IronIngot_C'\""
            ),
            "Desc_IronIngot_C"
        )
