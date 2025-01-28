from PySide6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QScrollArea, QSizePolicy

from .constraints_widget import ConstraintsWidget, Constraint

from satisfactoryobjects.resourceduplicatetypingsaver import resource_duplicate_typing_saver
# CAUTION: these better have been populated already, or things will definitely
# break
from satisfactoryobjects.itemhandler import items


def make_form_subsection_header(
    subsection_label: str,
    button_label: str = 'Add'
) -> tuple[QHBoxLayout, QPushButton]:
    '''Helper function to make the subsection header for a form'''
    subsection_header_layout = QHBoxLayout()
    subsection_header_layout.addWidget(QLabel(subsection_label))
    subsection_header_button = QPushButton(button_label)
    # make the button fill the space not occupied by the label
    subsection_header_button.setSizePolicy(
        QSizePolicy.Policy.MinimumExpanding,
        QSizePolicy.Policy.Fixed
    )
    subsection_header_layout.addWidget(subsection_header_button)
    return (subsection_header_layout, subsection_header_button)


class ProblemTabContent(QWidget):
    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(ProblemTabContent, self).__init__(*args, **kwargs)

        # Holds the scroll area and the run optimisation button
        layout = QVBoxLayout()

        # Holds the form frame, so it is scrollable
        form_container = QScrollArea()

        # allow the form to dynamically resize as items are added and removed,
        # rather than squashing new items
        form_container.setWidgetResizable(True)

        # Holds the layout used by the form.
        form_layout_container = QFrame()

        # At one point this was an actual QFormLayout, but I found that it was
        # easier to get the responsive design behaviour that I wanted by using
        # a QVBoxLayout as the outermost layout for the form.
        form_layout = QVBoxLayout(form_layout_container)

        # Production targets section

        # custom widget for production targets
        self.targets_widget = ConstraintsWidget()
        # start off with one target
        self.targets_widget.add_constraint(Constraint(items, default_value=1))
        # header for the production targets section
        (
            targets_section_header,
            add_target_button
        ) = make_form_subsection_header(
            'Target weightings'
        )

        # setup the callback to add new targets
        add_target_button.clicked.connect(self.add_target)
        # add the section header
        form_layout.addLayout(targets_section_header)
        # add the section content
        form_layout.addWidget(self.targets_widget)

        # Resource availability constraints section
        self.resource_availability_constraints_widget = ConstraintsWidget()
        # Start with one resource availability constraint per basic resource.
        # First, add the solid resources that are present in all versions of
        # the docs file (iron, caterium, copper, limestone, coal, quartz,
        # sulphur, uranium, bauxite).
        for resource in resource_duplicate_typing_saver(
            [
                "OreIron",
                "OreCopper",
                "Stone",  # Limestone
                "Coal",
                "OreGold",  # Caterium
                "Sulfur",
                "RawQuartz",
                "OreBauxite",
                "OreUranium"
            ]
        ):
            # As mentioned before, these resources are present in all versions
            # of the docs file that one would be likely to use (i.e. both
            # update 8 and release 1.0) and thus require no special checks for
            # presence, so don't bother with the dictionary lookup.
            # Although a user might have persisted a game installation from an
            # update before one of these resources was introduced, they are
            # likely not using external planners anyway due to lack of support
            # (i.e. I am providing game version support parity with popular
            # planners as of writing this) and I did not start playing
            # Satisfactory before update 8 was released (or maybe it was
            # update 7?  either way I don't have a copy of the docs file to
            # test with)
            self.resource_availability_constraints_widget.add_constraint(
                Constraint(items, resource)
            )
        # final ore node: SAM - this was not present in the update 8 docs file
        # and thus its existence must be first verified.
        # (this also can double as a heuristic for whether the docs file
        # provided was from the early access period i.e. before release 1.0)
        try:
            self.resource_availability_constraints_widget.add_constraint(
                # SAM (previously SAM ore)
                # Although present before 1.0, it doesnt seem to appear in
                # docs.json before then.  Since it wasnt possible to automate
                # at that time (nodes would run out until save reload) and no
                # use was yet implemented, it is more sensible to just ignore
                # it.
                # try-except with a lookup from the actual items dictionary to
                # detect if the docs file is pre or post 1.0
                Constraint(items, items["Desc_SAM_C"])
            )
        except KeyError:
            # pre 1.0 docs file, no SAM ore loaded
            # in these versions SAM ore existed but had no use and couldnt be
            # automated - miners would stop extracting after ~50 ore had been
            # extracted and would not restart until the game was reloaded.

            # see above - SAM ore doesnt exist in this version of the file and
            # is not relevant to production in the corresponding version of
            # the game.
            pass
        # Now that all the solid resources have been added, add the liquid
        # resources.  Although quite a few fluids were added for version 1.0
        # of the game, none of them are basic resources (my definition of
        # basic resource = has a corresponding node type or production
        # location is otherwise constrained, and this form of production is
        # not implemented as a recipe i.e. that one fluid with a zero-cost
        # recipe that version 1.0 added doesnt count as a basic resource since
        # you can place its production machine anywhere and it is technically
        # a recipe, but water is a basic resource since you can only put water
        # extractors in whatever the game considers to be deep enough water,
        # or get it from a resource well)
        for resource in resource_duplicate_typing_saver(
            [
                "Water",
                "LiquidOil",  # Crude oil
                "NitrogenGas"
            ]
        ):
            # Again, these resources are present in all versions of the docs
            # file that I have access to (and the only reason that I could see
            # for keeping an install from before update 8 would be for
            # speedrunning, and even then update 8 has its fair share of
            # speedrun glitches that one might keep an install for - now that
            # modding support has caught up to release 1.0 I can't see casual
            # players remaining on update 8 unless they really don't want to
            # fix anything that depends on the few late-game recipes that have
            # changed, and if a speedrunner was running an older version the
            # routing would likely be done manually and since update 8 had a
            # glitch (patched not due to its main effect of allowing infinite
            # production of literally anything with a defined recipe but due
            # to its side effect of sometimes crashing the game) that could
            # allow any machine to produce any recipe at max clock speed, at
            # the equivalent power consumption of min clock speed, and with no
            # resource consumption, such a planner is irrelevant to begin with)
            self.resource_availability_constraints_widget.add_constraint(
                Constraint(items, resource)
            )

        # create the header for the resource availability section
        (
            resource_availability_section_header,
            add_resource_availability_constraint_button
        ) = make_form_subsection_header(
            'Resource Availability'
        )
        # setup the callback to add new constraints
        add_resource_availability_constraint_button.clicked.connect(
            self.add_resource_availability_constraint
        )
        # add the section header
        form_layout.addLayout(
            resource_availability_section_header
        )
        # add the section content
        form_layout.addWidget(
            self.resource_availability_constraints_widget
        )

    def add_target(self):
        '''Adds a new production target to the production targets widget'''
        self.targets_widget.add_constraint(Constraint(items, default_value=1))

    def add_resource_availability_constraint(self):
        '''Adds a new resource availability constraint to the resource availability constraints widget'''
        self.resource_availability_constraints_widget.add_constraint(
            Constraint(items)
        )
