from PySide6.QtWidgets import QFormLayout, QCheckBox, QWidget, QHBoxLayout, QGridLayout, QGroupBox

from satisfactoryobjects.recipes import Recipe
# CAUTION: these better have been populated already, or things will definitely
# break
from satisfactoryobjects.recipehandler import recipes


class RecipeSelector(QGridLayout):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(RecipeSelector, self).__init__(*args, **kwargs)
        self.recipe_checkboxes: dict[str, QCheckBox] = dict()
        normal_group_box = QGroupBox('Normal')
        normal_form = QFormLayout()
        alternate_group_box = QGroupBox('Alternate')
        alternate_form = QFormLayout()
        # code to allow for alphabetical sorting
        recipe_names: list[tuple[str, str]] = [
            (recipe_key, recipe.user_facing_name)
            for recipe_key, recipe
            in recipes.items()
        ]
        # the key function defines a mapping between an item in the list and
        # the value that should be used for comparisons in sorting
        recipe_names.sort(
            key=lambda id_name_tuple: id_name_tuple[1]
        )
        for id_recipe_tuple in map(
            lambda id_name_tuple: (
                id_name_tuple[0],
                recipes[id_name_tuple[0]]
            ),
            recipe_names
        ):
            checkbox = QCheckBox()
            (
                alternate_form
                if id_recipe_tuple[1].is_alternate
                else normal_form
            ).addRow(
                id_recipe_tuple[1].user_facing_name, checkbox
            )
            # default config: enable all the default recipes (since these are
            # automatically available) but disable all the alternate recipes
            # (since these are unlocked individually and randomly by scanning
            # hard drives)
            checkbox.setChecked(not id_recipe_tuple[1].is_alternate)
            # will modify to be backed by something in the config

            # self.addRow(id_recipe_tuple[1].user_facing_name, checkbox)
            self.recipe_checkboxes[id_recipe_tuple[0]] = checkbox

        for group_box, form in (
            (normal_group_box, normal_form),
            (alternate_group_box, alternate_form)
        ):
            group_box.setLayout(form)

        self.addWidget(normal_group_box, 1, 0)
        self.addWidget(alternate_group_box, 1, 1)
