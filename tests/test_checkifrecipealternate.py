import unittest
from satisfactoryobjects import checkifrecipealternate


class TestCheckIfRecipeAlternate(unittest.TestCase):
    # checkifrecipealternate.py does not have logging, so no need to enable or
    # disable it
    def test_alternate_recipe_detected(self):
        self.assertTrue(checkifrecipealternate.check_if_recipe_alternate(
            'BlueprintGeneratedClass /Game/FactoryGame/Recipes/AlternateRecipes/New_Update3/Recipe_Alternate_WetConcrete.Recipe_Alternate_WetConcrete_C'
        ))

    def test_non_alternate_recipe_not_detected(self):
        self.assertFalse(checkifrecipealternate.check_if_recipe_alternate(
            'BlueprintGeneratedClass /Game/FactoryGame/Recipes/Constructor/Recipe_Fabric.Recipe_Fabric_C'
        ))

    def test_buildable_recipe_not_detected(self):
        # less important since these are skipped due to the program not caring
        # about the build gun and thus whether or not they are considered
        # alternate by the code is irrelevant
        self.assertFalse(checkifrecipealternate.check_if_recipe_alternate(
            'BlueprintGeneratedClass /Game/FactoryGame/Buildable/Building/Wall/ConcreteWallSet/Recipe_Wall_Concrete_8x1.Recipe_Wall_Concrete_8x1_C'
        ))
