import logging
from itertools import filterfalse
from .recipehandler import recipes
from .items import Item
from .recipes import Recipe
from .lookuperrors import RecipeLookupError

toplevel_logger = logging.getLogger(__name__)


def lookup_recipes(target_item: Item, lookup_consuming_recipes: bool = False) -> list[Recipe]:
    _ret: list[Recipe] = list()

    for recipe in recipes.values():
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


# probably will become disused
def lookup_production_chain(targets: list[Item]):
    # NOT YET COMPLETE
    for target in targets:
        source_recipes = lookup_recipes(target)
        for source_recipe in source_recipes:
            print(source_recipe)
            for dependency in source_recipe.dependencies:
                print("dependency")
                print(dependency.item)
            for product in filterfalse(
                lambda product: product.item == target,
                source_recipe.products
            ):
                print("byproduct")
                print(product.item)
