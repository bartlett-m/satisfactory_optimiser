from functools import partial

from PySide6.QtWidgets import QFormLayout, QCheckBox, QWidget, QHBoxLayout, QGridLayout, QGroupBox, QComboBox, QPushButton
from PySide6.QtCore import Qt, QSettings

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

        # ini settings are separate from the regular settings and are
        # guaranteed to be able to store large amounts of data in a single key
        # e.g. store an entire list (unlike the native format which may not be
        # able to e.g. on Windows where its a registry key)
        self.recipe_selection_persistence_obj = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            'bartlett-m',
            'Satisfactory Optimiser'
        )

        #self.recipe_selection_persistence_obj.setValue('recipes/alternate/TEST_EXAMPLE', 1)

        self.profile_name_combo_box = QComboBox()
        self.profile_name_combo_box.setEditable(True)

        self.load_profile_button = QPushButton('Load')
        self.save_profile_button = QPushButton('💾 Save')
        self.delete_profile_button = QPushButton('🗑 Delete')

        self.recipe_checkboxes: dict[str, QCheckBox] = dict()
        self.all_normal_recipe_checkbox = QCheckBox('All normal')
        self.all_alternate_recipe_checkbox = QCheckBox('All alternate')
        #for checkbox in (
        #    self.all_normal_recipe_checkbox,
        #    self.all_alternate_recipe_checkbox
        #):
        #    checkbox.setTristate(True)
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
        # to allow for setting the states of all the normal or all the
        # alternate recipe checkboxes
        self.normal_recipe_identifiers: set[str] = set()
        self.alternate_recipe_identifiers: set[str] = set()
        # to allow for determining if the all alternate or all normal
        # checkboxes need to be updated
        self.normal_recipes_available = 0
        self.alternate_recipes_available = 0
        self.normal_recipes_active = 0
        self.alternate_recipes_active = 0
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

            checkbox.checkStateChanged.connect(
                partial(
                    self.generic_recipe_checkbox_callback,
                    id_recipe_tuple[0],
                    id_recipe_tuple[1].is_alternate
                )
            )

            # self.addRow(id_recipe_tuple[1].user_facing_name, checkbox)
            self.recipe_checkboxes[id_recipe_tuple[0]] = checkbox

            if id_recipe_tuple[1].is_alternate:
                self.alternate_recipe_identifiers.add(id_recipe_tuple[0])
                self.alternate_recipes_available += 1
            else:
                self.normal_recipe_identifiers.add(id_recipe_tuple[0])
                self.normal_recipes_available += 1

        for group_box, form in (
            (normal_group_box, normal_form),
            (alternate_group_box, alternate_form)
        ):
            group_box.setLayout(form)

        self.addWidget(self.profile_name_combo_box, 0, 0)
        self.addWidget(self.load_profile_button, 0, 1)
        self.addWidget(self.save_profile_button, 0, 2)
        self.addWidget(self.delete_profile_button, 0, 3)
        self.addWidget(self.all_normal_recipe_checkbox, 1, 0, 1, 2)
        self.addWidget(self.all_alternate_recipe_checkbox, 1, 2, 1, 2)
        self.addWidget(normal_group_box, 2, 0, 1, 2)
        self.addWidget(alternate_group_box, 2, 2, 1, 2)

    def generic_recipe_checkbox_callback(
        self,
        recipe_checkbox_id: str,
        is_alternate: bool,
        check_state: Qt.CheckState
    ):
        print(recipe_checkbox_id)
        print(is_alternate)
        print(check_state)
        # REMEMBER: if setting a checkbox to partially checked then said
        # checkbox automatically becomes tristate
        # so will need to have a mechanism to unset that

    def recipe_category_checkbox_callback(
        self,
        is_alternate: bool,
        check_state: Qt.CheckState
    ):
        # REMEMBER: need some handling for tristate - perhaps automatically
        # disable it when set to a non-tristate value?
        pass
