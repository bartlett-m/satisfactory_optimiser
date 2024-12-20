import logging

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

        toplevel_logger.debug(f"Loading recipe {_class["ClassName"]}")
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
                # the three recipes using this dont make it clear how
                # its defined
                # it could be that the factor is the range and the constant
                # is the minimum, or it could be that the constant is half the
                # range and the factor is the average
                float(_class["mVariablePowerConsumptionFactor"])
            )
        except ItemLookupError:
            toplevel_logger.error(
                f"Skipping recipe {_class["ClassName"]} "
                "due to error looking up a resource"
            )
        except MachineLookupError:
            toplevel_logger.error(
                f"Skipping recipe {_class["ClassName"]} "
                "due to error looking up all machines"
            )
