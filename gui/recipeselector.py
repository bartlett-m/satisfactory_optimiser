from functools import partial

from PySide6.QtWidgets import QFormLayout, QCheckBox, QWidget, QHBoxLayout, QGridLayout, QGroupBox, QComboBox, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QSettings, QSignalBlocker

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
        self.profile_name_combo_box.addItem('default')
        # TODO: have the 'default' profile not be saveable over.  have a
        # 'user-default' profile that is used instead for this.  if this
        # profile exists, select this by default.  otherwise, load 'default'
        # (dynamically created at runtime as all normal recipes, no alternate
        # recipes)
        self.profile_name_combo_box.setEditable(True)
        n_user_defined_profiles = self.recipe_selection_persistence_obj.beginReadArray(
            'profile-names'
        )
        self.user_defined_profile_names: list[str] = list()
        for idx in range(n_user_defined_profiles):
            self.recipe_selection_persistence_obj.setArrayIndex(idx)
            profile_name = self.recipe_selection_persistence_obj.value('profile-name')
            self.user_defined_profile_names.append(profile_name)
            self.profile_name_combo_box.addItem(profile_name)
            if profile_name == 'user-default':
                # +1 to account for the fact that there is already the
                # 'default' profile
                self.profile_name_combo_box.setCurrentIndex(idx+1)
            print(profile_name)
        self.recipe_selection_persistence_obj.endArray()


        self.load_profile_button = QPushButton('Load')
        self.load_profile_button.clicked.connect(self.load_profile_callback)
        self.save_profile_button = QPushButton('💾 Save')
        self.save_profile_button.clicked.connect(self.save_profile_callback)
        self.delete_profile_button = QPushButton('🗑 Delete')
        self.delete_profile_button.clicked.connect(
            self.delete_profile_callback
        )

        self.recipe_checkboxes: dict[str, QCheckBox] = dict()
        self.all_normal_recipe_checkbox = QCheckBox('All normal')
        self.all_normal_recipe_checkbox.checkStateChanged.connect(
            partial(
                self.recipe_category_checkbox_callback,
                False
            )
        )
        self.all_alternate_recipe_checkbox = QCheckBox('All alternate')
        self.all_alternate_recipe_checkbox.checkStateChanged.connect(
            partial(
                self.recipe_category_checkbox_callback,
                True
            )
        )
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

        self.load_profile_callback(internal_use_internal_load=True)

    def generic_recipe_checkbox_callback(
        self,
        # TODO: this parameter doesnt actually seem to be that useful
        recipe_checkbox_id: str,
        is_alternate: bool,
        check_state: Qt.CheckState
    ):
        #print(recipe_checkbox_id)
        #print(is_alternate)
        #print(check_state)
        # REMEMBER: if setting a checkbox to partially checked then said
        # checkbox automatically becomes tristate
        # so will need to have a mechanism to unset that
        # also fun issue i found: when using setChecked on a checkbox that is
        # initially in the PartiallyChecked state, it wont update until
        # hovered over.  using setCheckState fixes this.
        if is_alternate and check_state == Qt.CheckState.Checked:
            self.alternate_recipes_active += 1
            if self.alternate_recipes_available == self.alternate_recipes_active:
                self.all_alternate_recipe_checkbox.setCheckState(
                    Qt.CheckState.Checked
                )
                # will fire recipe_category_checkbox_callback and we can set
                # it to not be tristate there
            else:
                self.all_alternate_recipe_checkbox.setCheckState(
                    Qt.CheckState.PartiallyChecked
                )
        elif is_alternate and check_state == Qt.CheckState.Unchecked:
            self.alternate_recipes_active -= 1
            if self.alternate_recipes_active == 0:
                self.all_alternate_recipe_checkbox.setCheckState(
                    Qt.CheckState.Unchecked
                )
                # see above - turning off tristate will be handled elsewhere
            else:
                self.all_alternate_recipe_checkbox.setCheckState(
                    Qt.CheckState.PartiallyChecked
                )
        elif (not is_alternate) and check_state == Qt.CheckState.Checked:
            self.normal_recipes_active += 1
            if self.normal_recipes_available == self.normal_recipes_active:
                self.all_normal_recipe_checkbox.setCheckState(
                    Qt.CheckState.Checked
                )
                # see above - turning off tristate will be handled elsewhere
            else:
                self.all_normal_recipe_checkbox.setCheckState(
                    Qt.CheckState.PartiallyChecked
                )
        else:  # by process of elimination...
            self.normal_recipes_active -= 1
            if self.normal_recipes_active == 0:
                self.all_normal_recipe_checkbox.setCheckState(
                    Qt.CheckState.Unchecked
                )
                # see above - turning off tristate will be handled elsewhere
            else:
                self.all_normal_recipe_checkbox.setCheckState(
                    Qt.CheckState.PartiallyChecked
                )

    def recipe_category_checkbox_callback(
        self,
        is_alternate: bool,
        check_state: Qt.CheckState
    ):
        # REMEMBER: need some handling for tristate - perhaps automatically
        # disable it when set to a non-tristate value?
        # ALSO REMEMBER: if check_state is tristate, assume it was manually
        # set to be that somewhere else (i.e. this is expected because of how
        # these signals work) - just return early in that case
        # ALSO REMEMBER: this only gets fired if the check state *changes* i.e.
        # if the check state is set to the state it already was then this does
        # NOT get called, which is actually quite convenient
        if check_state == Qt.CheckState.PartiallyChecked:
            return

        firing_checkbox = (
            self.all_alternate_recipe_checkbox
            if is_alternate
            else self.all_normal_recipe_checkbox
        )

        # block signals to prevent an infinite loop where the check state of
        # this checkbox is repeatedly changed by the signal handlers for the
        # individual recipe checkboxes and then that change causes the
        # individual recipe checkboxes to be repeatedly changed themselves...
        # you see where this is going
        with QSignalBlocker(
            firing_checkbox
        ):
            for identifier in (
                self.alternate_recipe_identifiers
                if is_alternate
                else self.normal_recipe_identifiers
            ):
                self.recipe_checkboxes[identifier].setCheckState(
                    check_state
                )
        # this has to be at the end.  i reckon setCheckState enables tristate
        # itself before sending the signal or whatever but i have no idea.
        # could also be some delay in a signal causing it to get blocked.
        # either way, if this is before the individual recipe checkboxes are
        # set (i.e. outside of the context-managed QSignalBlocker), it doesn't
        # work, but it does work if its here.
        firing_checkbox.setTristate(False)

    def load_profile_callback(self, internal_use_internal_load: bool = False):
        profile_name = self.profile_name_combo_box.currentText()
        profile_is_legit = self.recipe_selection_persistence_obj.value(
            'profile/' + profile_name + '/is-legit'
        ) == 'yes'
        if (not profile_is_legit) and profile_name == 'user-default' and internal_use_internal_load:
            msg_box = QMessageBox(None)
            msg_box.setWindowTitle('Satisfactory Optimiser')
            msg_box.setText(
                'User-specified default profile is corrupted!  '
                'Falling back to default profile.'
            )
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setIcon(QMessageBox.Icon.Critical)

            _ = msg_box.exec()

            self.profile_name_combo_box.setCurrentIndex(0)
            profile_name = 'default'
        elif (not profile_is_legit) and profile_name != 'default':
            # error: trying to load non-existent profile
            # TODO: special handling for default profile if not exists i.e.
            # create it
            msg_box = QMessageBox(None)
            msg_box.setWindowTitle('Satisfactory Optimiser')
            msg_box.setText(
                'Cannot load non-existent profile "' + profile_name + '"'
            )
            msg_box.setStandardButtons(QMessageBox.StandardButton.Abort)
            msg_box.setIcon(QMessageBox.Icon.Critical)

            _ = msg_box.exec()
            return

        self.all_normal_recipe_checkbox.setChecked(False)
        self.all_alternate_recipe_checkbox.setChecked(False)
        for recipe_id, recipe_checkbox in self.recipe_checkboxes.items():
            is_alternate = recipe_id in self.alternate_recipe_identifiers
            check_state = self.recipe_selection_persistence_obj.value(
                'profile/' + profile_name + '/recipes/' +
                ('alternate' if is_alternate else 'normal') + '/' + recipe_id
            )
            if check_state == '1':
                recipe_checkbox.setChecked(True)
            elif check_state == '0':
                recipe_checkbox.setChecked(False)
            else:
                # load default
                recipe_checkbox.setChecked(not is_alternate)
        if self.normal_recipes_active == self.normal_recipes_available:
            self.all_normal_recipe_checkbox.setChecked(True)
            self.all_normal_recipe_checkbox.setTristate(False)
        elif self.normal_recipes_active == 0:
            self.all_normal_recipe_checkbox.setChecked(False)
            self.all_normal_recipe_checkbox.setTristate(False)
        else:
            self.all_normal_recipe_checkbox.setCheckState(
                Qt.CheckState.PartiallyChecked
            )
        if (
            self.alternate_recipes_active
            ==
            self.alternate_recipes_available
        ):
            self.all_alternate_recipe_checkbox.setChecked(True)
            self.all_alternate_recipe_checkbox.setTristate(False)
        elif self.alternate_recipes_active == 0:
            self.all_alternate_recipe_checkbox.setChecked(False)
            self.all_alternate_recipe_checkbox.setTristate(False)
        else:
            self.all_alternate_recipe_checkbox.setCheckState(
                Qt.CheckState.PartiallyChecked
            )

    def save_profile_callback(self) -> None:
        profile_name = self.profile_name_combo_box.currentText()
        if profile_name == 'default':
            # error: trying to overwrite default profile
            msg_box = QMessageBox(None)
            msg_box.setWindowTitle('Satisfactory Optimiser')
            msg_box.setText(
                'Trying to overwrite the built-in default profile!\n'
                'Hint: You can create a profile named "user-default", which '
                'will load instead of the built-in default profile on '
                'application start.\n'
                'Hint: To create a new profile, type its name into the profile'
                ' selection dropdown and then click the Save button.'
            )
            msg_box.setStandardButtons(QMessageBox.StandardButton.Abort)
            msg_box.setIcon(QMessageBox.Icon.Critical)

            _ = msg_box.exec()
            return
        profile_idx_from_edit_text = self.profile_name_combo_box.findText(
            profile_name
        )
        new_profile = profile_idx_from_edit_text == -1
        if new_profile:
            self.user_defined_profile_names.append(profile_name)
            self.profile_name_combo_box.addItem(profile_name)
            new_profile_name_combo_box_index = len(
                self.user_defined_profile_names
            )
            self.recipe_selection_persistence_obj.beginWriteArray(
                'profile-names', new_profile_name_combo_box_index
            )
            self.recipe_selection_persistence_obj.setArrayIndex(
                new_profile_name_combo_box_index-1
            )
            self.recipe_selection_persistence_obj.setValue(
                'profile-name',
                profile_name
            )
            self.recipe_selection_persistence_obj.endArray()
        for recipe_id_set, recipe_set_prefix in (
            (self.normal_recipe_identifiers, 'normal'),
            (self.alternate_recipe_identifiers, 'alternate')
        ):
            for recipe_id in recipe_id_set:
                self.recipe_selection_persistence_obj.setValue(
                    'profile/' + profile_name + '/recipes/' +
                    recipe_set_prefix + '/' + recipe_id,
                    (
                        '1'
                        if (
                            self.recipe_checkboxes[recipe_id].checkState()
                            ==
                            Qt.CheckState.Checked
                        )
                        else '0'
                    )
                )
        self.recipe_selection_persistence_obj.setValue(
            'profile/' + profile_name + '/is-legit',
            'yes'
        )

    def delete_profile_callback(self) -> None:
        profile_name = self.profile_name_combo_box.currentText()
        profile_idx = self.profile_name_combo_box.currentIndex()
        if self.profile_name_combo_box.findText(profile_name) != profile_idx:
            # error: user typed in a profile that does not exist and is likely
            # not trying to delete the currently indexed profile
            msg_box = QMessageBox(None)
            msg_box.setWindowTitle('Satisfactory Optimiser')
            msg_box.setText(
                'Trying to delete a non-existent profile (presumably)!  '
                'Aborted to prevent accidental deletion of another profile!'
            )
            msg_box.setStandardButtons(QMessageBox.StandardButton.Abort)
            msg_box.setIcon(QMessageBox.Icon.Critical)

            _ = msg_box.exec()
            return
        elif profile_name == 'default':
            # error: user attempting to delete the default profile
            msg_box = QMessageBox(None)
            msg_box.setWindowTitle('Satisfactory Optimiser')
            msg_box.setText(
                'Cannot delete the built-in default profile!'
            )
            msg_box.setStandardButtons(QMessageBox.StandardButton.Abort)
            msg_box.setIcon(QMessageBox.Icon.Critical)

            _ = msg_box.exec()
            return
        self.recipe_selection_persistence_obj.remove('profile/' + profile_name)
        self.user_defined_profile_names.remove(profile_name)
        self.profile_name_combo_box.removeItem(profile_idx)
        # set the selection back to the now-removed profile to prevent any
        # confusion on the part of the user (since the combo box is editable,
        # this is perfectly fine.  it also allows the user to undo a removal
        # by clicking save)
        self.profile_name_combo_box.setEditText(profile_name)
        self.recipe_selection_persistence_obj.beginWriteArray(
            'profile-names', len(self.user_defined_profile_names)
        )
        for idx, name in enumerate(self.user_defined_profile_names):
            self.recipe_selection_persistence_obj.setArrayIndex(idx)
            self.recipe_selection_persistence_obj.setValue('profile-name', name)
        # purge the leftover element which is now out of array bounds
        # if this element wasnt the one being deleted, it will have been
        # shifted in bounds by the above loop
        self.recipe_selection_persistence_obj.setArrayIndex(
            len(self.user_defined_profile_names)
        )
        self.recipe_selection_persistence_obj.remove('profile-name')
        self.recipe_selection_persistence_obj.endArray()
