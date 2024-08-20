import logging
from .recipehandler import recipes
from .items import Item
from .recipes import Recipe
from .lookuperrors import RecipeLookupError

toplevel_logger = logging.getLogger(__name__)


def lookup_recipes(target_item: Item) -> list[Recipe]:
    _ret: list[Recipe] = list()

    for _, recipe in recipes.items():
        for resource in recipe.products:
            if resource.item == target_item:
                _ret.append(recipe)
                # I sure hope no recipe has the same product twice
                break

    if len(_ret) == 0:
        raise RecipeLookupError(
            f"No recipes produce item {target_item}"
        )

    return _ret
