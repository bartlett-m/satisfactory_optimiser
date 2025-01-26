# this stuff will eventually be barely-documented environment variables or
# something


# its meant to provide defaults for gui properties that can't automatically be
# determined at runtime or otherwise (e.g. max decimals for double spinbox
# that doesnt result in imprecision) that are powerful enough to give users
# freedom, but without leading to possible undefined or unexpected behaviour
# (e.g. value truncation)

# the number of decimals on double spinboxes that are supposed to lack limits
# on precision
# in this case it was selected to be the same as the precision of the "clock
# speed" value in-game
# (see https://satisfactory.wiki.gg/wiki/Clock_speed#Precision)
SUPPOSEDLY_UNLIMITED_DOUBLE_SPINBOX_MAX_DECIMALS = 4

# Stretch factor that the detailed view of the solution is given in the
# QSplitter (well SolutionTabContent), that contains it.
# Just a very large number so that in practice the quick overview is at
# minimum size.  Increase if you have a *comically large* display and this
# doesn't behave as intended.
LARGE_STRETCH_FACTOR_CONSTANT = 1 << 16
