import unittest
from fractions import Fraction
from optimisationsolver import simplex
from utils.variabletypetags import VariableType, AnonymousTypeTag, NamedTypeTag


class TestTableau(unittest.TestCase):
    def tableau_0(self) -> simplex.Tableau:
        return simplex.Tableau(
            inequalities=[
                simplex.Inequality([simplex.Variable(0, 1), simplex.Variable(1, 1)], 40),
                simplex.Inequality([simplex.Variable(0, 4), simplex.Variable(1, 1)], 100),
                simplex.ObjectiveEquation([simplex.Variable(0, -20), simplex.Variable(1, -10)], 0, 1)
            ]
        )

    def tableau_1(self) -> simplex.Tableau:
        return simplex.Tableau(
            inequalities=[
                simplex.Inequality([simplex.Variable("x", 1), simplex.Variable("y", 1), simplex.Variable("z", 1)], 10),
                simplex.Inequality([simplex.Variable("x", 2), simplex.Variable("y", -1)], 0),
                simplex.Inequality([simplex.Variable("x", -1), simplex.Variable("y", -3), simplex.Variable("z", 1)], 6),
                simplex.ObjectiveEquation([simplex.Variable("x", -5), simplex.Variable("y", 3), simplex.Variable("z", -4)], 0, 1)
            ]
        )

    def test_constructor_does_not_error_0(self):
        self.tableau_0()

    def test_initialise_values_0(self):
        t = self.tableau_0()

        self.assertCountEqual(
            t.get_variable_values(),
            [
                (NamedTypeTag(VariableType.NORMAL, 0), 0),
                (NamedTypeTag(VariableType.NORMAL, 1), 0),
                (NamedTypeTag(VariableType.SLACK, 0), 40),
                (NamedTypeTag(VariableType.SLACK, 1), 100),
                (AnonymousTypeTag(VariableType.OBJECTIVE), 0)
            ]
        )

    def test_solve_and_report_values_0(self):
        t = self.tableau_0()
        t.pivot_until_done()

        self.assertCountEqual(
            t.get_variable_values(),
            [
                (NamedTypeTag(VariableType.NORMAL, 0), 20),
                (NamedTypeTag(VariableType.NORMAL, 1), 20),
                (NamedTypeTag(VariableType.SLACK, 0), 0),
                (NamedTypeTag(VariableType.SLACK, 1), 0),
                (AnonymousTypeTag(VariableType.OBJECTIVE), 600)
            ]
        )

        # self.assertEqual(
        #     t._tableau,
        #     [
        #         [0, 1, Fraction(4, 3), Fraction(-1, 3), 0, 20],
        #         [1, 0, Fraction(-1, 3), Fraction(1, 3), 0, 20],
        #         [0, 0, Fraction(20, 3), Fraction(10, 3), 1, 600]
        #     ]
        # )
        # it looks like the video i got the example from is incorrect
        # (tested algorithm by hand)
        # so the -1/3 in col 4 row 2 is now +1/3
        # and the 15/4 in col 4 row 3 is now 10/3

    def test_constructor_does_not_error_1(self):
        self.tableau_1()

    def test_initialise_values_1(self):
        # TODO: figure out if theres a way to automatically skip this test if
        # test_constructor_does_not_error_1 fails (since this test is a
        # superset of that test)
        t = self.tableau_1()
        # see test_solve_and_report_values_2 comments
        self.assertCountEqual(
            t.get_variable_values(),
            [
                (NamedTypeTag(VariableType.NORMAL, 'x'), 0),
                (NamedTypeTag(VariableType.NORMAL, 'y'), 0),
                (NamedTypeTag(VariableType.NORMAL, 'z'), 0),
                (NamedTypeTag(VariableType.SLACK, 0), 10),
                (NamedTypeTag(VariableType.SLACK, 1), 0),
                (NamedTypeTag(VariableType.SLACK, 2), 6),
                (AnonymousTypeTag(VariableType.OBJECTIVE), 0)
            ]
        )

    def test_solve_and_report_values_1(self):
        # from original version of this test:

        # When pivoting, this test will try a division by zero unless row
        # ratios resulting in a zero divison are filtered.  This division by
        # zero will occur on the second pivot.  If the row with the zero
        # division ratio is used as the pivot row, then it will also result
        # in a zero division during the actual pivot.
        #
        # The fourth iteration additionally returns to the second iteration in
        # this tableau i.e. it will cycle.  This is not prevented by using
        # Bland's rule.  This is as the cycling is caused because my prior
        # implementation of the algorithm pivots on a row with a negative
        # pivot element if the right-hand-side is zero, however it should only
        # pivot on a row with a right-hand-side of zero if the pivot element
        # is positive.  My new implementation of the algorithm now checks for
        # this specific case and skips such rows.

        # the above is not guaranteed to be exactly true if the constructor is
        # ever changed to lay out the variables differently
        t = self.tableau_1()
        t.pivot_until_done()
        self.assertCountEqual(
            t.get_variable_values(),
            [
                (NamedTypeTag(VariableType.NORMAL, 'x'), Fraction(2, 5)),
                (NamedTypeTag(VariableType.NORMAL, 'y'), Fraction(4, 5)),
                (NamedTypeTag(VariableType.NORMAL, 'z'), Fraction(44, 5)),
                (NamedTypeTag(VariableType.SLACK, 0), 0),
                (NamedTypeTag(VariableType.SLACK, 1), 0),
                (NamedTypeTag(VariableType.SLACK, 2), 0),
                (AnonymousTypeTag(VariableType.OBJECTIVE), Fraction(348, 10))
            ]
        )

    def test_solve_and_report_values_2(self):
        # actually just me doing further maths discrete classwork
        # but i found some bugs in my new constructor so it was useful
        # i was then able to turn this into an actual test using the new
        # constructor and value reporting function
        # print("test_temp")

        # i think i already have enough tests of initialisation, so i wont
        # reuse this tableau for other tests - therefore i will just define it
        # here and not at the start of the test class
        t = simplex.Tableau(
            inequalities=[
                simplex.Inequality([simplex.Variable("x", 5), simplex.Variable("y", 7)], 35),
                simplex.Inequality([simplex.Variable("x", 4), simplex.Variable("y", 9)], 36),
                simplex.ObjectiveEquation([simplex.Variable("x", -2), simplex.Variable("y", -3)], 0, 1)
            ]
        )
        t.pivot_until_done()
        # based on what desmos said doing this program graphically
        # the output it gave looks correct

        # [Fraction(1, 1), Fraction(0, 1), Fraction(9, 17), Fraction(-7, 17), Fraction(0, 1), Fraction(63, 17)]
        # [Fraction(0, 1), Fraction(1, 1), Fraction(-4, 17), Fraction(5, 17), Fraction(0, 1), Fraction(40, 17)]
        # [Fraction(0, 1), Fraction(0, 1), Fraction(6, 17), Fraction(1, 17), Fraction(1, 1), Fraction(246, 17)]

        # print(t._get_variable_value(1))
        # print(t.get_variable_values())

        # assertCountEqual is NOT checking whether the length of the two lists
        # is the same.
        # it instead checks that each unique item in the list occurs the same
        # number of times.
        # i.e. it checks if the lists are equal as if list was an unordered
        # datatype rather than an ordered one, which is what i want since the
        # returned variable values would not need to be in any particular
        # order in practice (although as of writing my api does return them in
        # a consistent order when sortable variable identifiers are used)
        self.assertCountEqual(
            t.get_variable_values(),
            [
                (NamedTypeTag(VariableType.NORMAL, 'x'), Fraction(63, 17)),
                (NamedTypeTag(VariableType.NORMAL, 'y'), Fraction(40, 17)),
                (NamedTypeTag(VariableType.SLACK, 0), 0),
                # this being out of order is to check if python ever changes
                # the behaviour of assertCountEqual and also to show that
                # assertCountEqual does not care about ordering
                # as of writing, these last two lines are swapped compared to
                # the actual order simplex returns
                (AnonymousTypeTag(VariableType.OBJECTIVE), Fraction(246, 17)),
                (NamedTypeTag(VariableType.SLACK, 1), 0)
            ]
        )

        # for row in t._tableau:
        #     print(row)

    def test_solve_and_report_values_with_intermediates(self):
        # this tests how the algorithm works (or doesnt work) when the tableau
        # is built directly on the graph-like data structure that the
        # docs.json parser creates, instead of preprocessing the inputs,
        # recipes etc into a smaller number of constraints so that effectively
        # only the penultimate recipe is directly considered (which would have
        # been hard to debug the generation of and would have driven me insane)

        # thanks to the fact that the algorithm can process this, i can
        # greatly simplify the problem construction code.

        # here we have:
        # x, y, z are available items input in the interface (we have 4 of x, 6 of y, and 2 of z)
        # f is a recipe.  it takes 3 of item b, and 1 of item c, and produces 2 of item a
        # a, b, c are the items x, y, z (but including production from recipes, which in this case only affects a)
        # we are trying to make the most a we can
        t = simplex.Tableau(
            [
                # there are 4 of x (item a) available
                simplex.Inequality([simplex.Variable('x', 1)], 4),
                # there are 6 of y (item b) available
                simplex.Inequality([simplex.Variable('y', 1)], 6),
                # there are 2 of z (item c) available
                simplex.Inequality([simplex.Variable('z', 1)], 2),
                # item a is produced by recipe f, which makes 2 of it
                simplex.Inequality([simplex.Variable('a', 1), simplex.Variable('x', -1), simplex.Variable('f', -2)], 0),
                # item b has no recipes producing it.
                simplex.Inequality([simplex.Variable('b', 1), simplex.Variable('y', -1)], 0),
                # item c has no recipes producing it.
                simplex.Inequality([simplex.Variable('c', 1), simplex.Variable('z', -1)], 0),
                # 3 of item b is used in recipe f.  item b is not used in any other recipes.
                simplex.Inequality([simplex.Variable('f', 3), simplex.Variable('b', -1)], 0),
                # 1 of item c is used in recipe f.  item c is not used in any other recipes.
                simplex.Inequality([simplex.Variable('f', 1), simplex.Variable('c', -1)], 0),
                # make as much of item a as possible
                simplex.ObjectiveEquation([simplex.Variable('a', -1)])
            ]
        )

        t.pivot_until_done()

        self.assertCountEqual(
            t.get_variable_values(),
            [
                # actual item variables (total number of items drawn into recipes or used as output)
                # note that the next three will show the total item flow
                # these return nonzero values even if the slack variables are nonzero (i.e. either there is excess input or excess production as a byproduct)
                # we have 8 of a being used/output
                (NamedTypeTag(VariableType.NORMAL, 'a'), 8),
                # we have 6 of b being used/output
                (NamedTypeTag(VariableType.NORMAL, 'b'), 6),
                # we have 2 of c being used/output
                (NamedTypeTag(VariableType.NORMAL, 'c'), 2),
                # we are using recipe f 2 times
                (NamedTypeTag(VariableType.NORMAL, 'f'), 2),
                # input variables
                # note that the next three will show the total item draw from what is manually input
                # these return nonzero values even if the slack variables are nonzero (i.e. there is excess input)
                # we drew 4 of item a from our input x
                (NamedTypeTag(VariableType.NORMAL, 'x'), 4),
                # we drew 6 of item b from our input y
                (NamedTypeTag(VariableType.NORMAL, 'y'), 6),
                # we drew 2 of item c from our input z
                (NamedTypeTag(VariableType.NORMAL, 'z'), 2),
                # slack variables
                (NamedTypeTag(VariableType.SLACK, 0), 0),
                (NamedTypeTag(VariableType.SLACK, 1), 0),
                (NamedTypeTag(VariableType.SLACK, 2), 0),
                (NamedTypeTag(VariableType.SLACK, 3), 0),
                (NamedTypeTag(VariableType.SLACK, 4), 0),
                (NamedTypeTag(VariableType.SLACK, 5), 0),
                (NamedTypeTag(VariableType.SLACK, 6), 0),
                (NamedTypeTag(VariableType.SLACK, 7), 0),
                # our objective was 8 (in this case, without weightings being implemented, that would mean that we have 8 of item a at the end)
                (AnonymousTypeTag(VariableType.OBJECTIVE), 8)
            ]
        )
