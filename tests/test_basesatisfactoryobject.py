import unittest
from satisfactoryobjects import basesatisfactoryobject


class TestBaseSatisfactoryObject(unittest.TestCase):
    # basesatisfactoryobject.py does not have logging, so no need to enable or
    # disable it

    def test_base_satisfactory_object_is_hashable(self):
        # If it is unhashable, it is impossible for classes that inherit from
        # it to be hashable (some of those classes need to be hashable)
        hash(
            basesatisfactoryobject.BaseSatisfactoryObject(
                "dummy_data",
                "Some user facing name for an object under test"
            )
        )

    def test_base_satisfactory_object_has_consistent_hash_value(self):
        # The hash value for the same object must logically be the same after
        # every calculation
        object_under_test = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for an object under test"
        )

        calculated_hash_1 = hash(object_under_test)
        calculated_hash_2 = hash(object_under_test)

        self.assertEqual(calculated_hash_1, calculated_hash_2)

    def test_equal_base_satisfactory_objects_have_consistent_hash_value(self):
        # Due to the implementation of __eq__, the hash value should be
        # consistent for objects that are equal.
        # Note that the reverse is not true (see following reference)
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # [accessed 2024-12-30 at 13:02]
        object_under_test_1 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for an object under test"
        )
        object_under_test_2 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for an object under test"
        )
        self.assertEqual(
            hash(object_under_test_1),
            hash(object_under_test_2)
        )

    def test_base_satisfactory_object_equality_comparison_0(self):
        object_under_test_1 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for an object under test"
        )
        object_under_test_2 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for an object under test"
        )
        self.assertEqual(
            object_under_test_1,
            object_under_test_2
        )

    def test_base_satisfactory_object_equality_comparison_1(self):
        object_under_test_1 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data_1",
            "Some user facing name for an object under test"
        )
        object_under_test_2 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data_2",
            "Some user facing name for an object under test"
        )
        self.assertNotEqual(
            object_under_test_1,
            object_under_test_2
        )

    def test_base_satisfactory_object_equality_comparison_2(self):
        object_under_test_1 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for a first object under test"
        )
        object_under_test_2 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data",
            "Some user facing name for a second object under test"
        )
        self.assertNotEqual(
            object_under_test_1,
            object_under_test_2
        )

    def test_base_satisfactory_object_equality_comparison_3(self):
        object_under_test_1 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data_1",
            "Some user facing name for a first object under test"
        )
        object_under_test_2 = basesatisfactoryobject.BaseSatisfactoryObject(
            "dummy_data_2",
            "Some user facing name for a second object under test"
        )
        self.assertNotEqual(
            object_under_test_1,
            object_under_test_2
        )
