import logging
from .recipehandler import recipes
from .items import Item
from .recipes import Recipe
from .lookuperrors import RecipeLookupError

toplevel_logger = logging.getLogger(__name__)


def lookup_recipes(
    target_item: Item,
    lookup_consuming_recipes: bool = False,
    # set would make more sense - if Recipe were hashable.
    disabled_recipes: list[Recipe] = []
) -> list[Recipe]:
    _ret: list[Recipe] = list()

    for recipe in recipes.values():
        if recipe in disabled_recipes:
            # could have some handler to give a more meaningful error if no
            # enabled recipes produce the resource, but this will function
            continue
        for resource in (
            recipe.dependencies
            if lookup_consuming_recipes
            else recipe.products
        ):
            if resource.item == target_item:
                _ret.append(recipe)
                # I sure hope no recipe has the same product twice
                break

    if len(_ret) == 0:
        raise RecipeLookupError(
            'No recipes '
            f'{("consum" if lookup_consuming_recipes else "produc")}'
            f'e item {target_item}'
        )

    return _ret
