import logging

from .checkifrecipealternate import check_if_recipe_alternate
from .recipes import Recipe
from .lookuperrors import ItemLookupError, MachineLookupError

toplevel_logger = logging.getLogger(__name__)

recipes: dict[str, Recipe] = dict()


def handler(obj):
    toplevel_logger.debug((obj["Classes"][0]))
    for _class in obj["Classes"]:
        # toplevel_logger.debug(_class["mDisplayName"])
        # toplevel_logger.debug(_class["mIngredients"])
        # recipes.append(_class["mIngredients"])

        toplevel_logger.debug(f'Loading recipe {_class["ClassName"]}')
        try:
            recipes[_class["ClassName"]] = Recipe(
                _class["ClassName"],
                _class["mDisplayName"],
                Recipe.parse_resources(
                    _class["mIngredients"],
                    _class["ClassName"]
                ),
                Recipe.parse_resources(
                    _class["mProduct"],
                    _class["ClassName"]
                ),
                Recipe.parse_produced_in(
                    _class["mProducedIn"],
                    _class["ClassName"]
                ),
                float(_class["mManufactoringDuration"]),  # [sic]
                # the three recipes using this in update 8 didnt make it clear
                # how variable power is defined
                # it could be that the factor is the range and the constant
                # is the minimum, or it could be that the constant is half the
                # range and the factor is the average
                # however some of the new release 1.0 recipes (such as all
                # those that are currently made in the converter) clarify
                # things:
                # the lowest power consumption is defined as the power
                # consumption constant
                # the highest power consumption is defined as the sum of the
                # power consumption constant and the power consumption factor
                # in other words: the constant is the lowest power consumption
                # and the factor is the range of power consumption
                # for our purposes, we dont need to worry about the
                # fluctuation, only the average power.  the machine starts at
                # its average power and ends at its average power in each
                # cycle, and changes linearly (so the average power
                # consumption is always the constant plus half the factor)
                (
                    float(_class['mVariablePowerConsumptionConstant'])
                    +
                    (float(_class['mVariablePowerConsumptionFactor'])/2)
                ),
                is_alternate=check_if_recipe_alternate(
                    _class['FullName']
                )
            )
        except ItemLookupError:
            toplevel_logger.error(
                f'Skipping recipe {_class["ClassName"]} '
                "due to error looking up a resource"
            )
        except MachineLookupError:
            toplevel_logger.error(
                f'Skipping recipe {_class["ClassName"]} '
                "due to error looking up all machines"
            )
