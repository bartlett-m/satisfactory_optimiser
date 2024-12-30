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
