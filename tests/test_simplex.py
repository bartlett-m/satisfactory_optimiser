import unittest
from fractions import Fraction
from optimisationsolver import simplex
from utils.variabletypetags import VariableType, AnonymousTypeTag, NamedTypeTag


class TestTableau(unittest.TestCase):
    def test_initialise_temp(self):
        t = simplex.Tableau()
        self.assertEqual(
            t._tableau,
            [
                [1, 1, 1, 0, 0, 40],
                [4, 1, 0, 1, 0, 100],
                [-20, -10, 0, 0, 1, 0]
            ]
        )

    def test_solve_temp(self):
        t = simplex.Tableau()
        t.pivot_until_done()
        self.assertEqual(
            t._tableau,
            [
                [0, 1, Fraction(4, 3), Fraction(-1, 3), 0, 20],
                [1, 0, Fraction(-1, 3), Fraction(1, 3), 0, 20],
                [0, 0, Fraction(20, 3), Fraction(10, 3), 1, 600]
            ]
        )
        # it looks like the video i got the example from is incorrect
        # (tested algorithm by hand)
        # so the -1/3 in col 4 row 2 is now +1/3
        # and the 15/4 in col 4 row 3 is now 10/3

    def test_solve_1(self):
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
        t = simplex.Tableau(
            [
                simplex.TableauRow([Fraction(x) for x in [1, 1, 1, 1, 0, 0, 0, 10]]),
                simplex.TableauRow([Fraction(x) for x in [2, -1, 0, 0, 1, 0, 0, 0]]),
                simplex.TableauRow([Fraction(x) for x in [-1, -3, 1, 0, 0, 1, 0, 6]]),
                simplex.TableauRow([Fraction(x) for x in [-5, 3, -4, 0, 0, 0, 1, 0]])
            ]
        )
        t.pivot_until_done()
        self.assertEqual(
            t._tableau,
            [
                [0, 1, 0, Fraction(1, 5), Fraction(-1, 5), Fraction(-1, 5), 0, Fraction(4, 5)],
                [1, 0, 0, Fraction(1, 10), Fraction(2, 5), Fraction(-1, 10), 0, Fraction(2, 5)],
                [0, 0, 1, Fraction(7, 10), Fraction(-1, 5), Fraction(3, 10), 0, Fraction(44, 5)],
                [0, 0, 0, Fraction(27, 10), Fraction(9, 5), Fraction(13, 10), 1, Fraction(348, 10)]
            ]
        )

    def test_constructor_does_not_error_1(self):
        _ = simplex.Tableau(
            inequalities=[
                simplex.Inequality([simplex.Variable("x", 1), simplex.Variable("y", 1), simplex.Variable("z", 1)], 10),
                simplex.Inequality([simplex.Variable("x", 2), simplex.Variable("y", -1)], 0),
                simplex.Inequality([simplex.Variable("x", 1), simplex.Variable("y", 3), simplex.Variable("z", -1)], -6),
                simplex.ObjectiveEquation([simplex.Variable("x", -5), simplex.Variable("y", 3), simplex.Variable("z", -4)], 0, 1)
            ]
        )

    def test_initialise_values_1(self):
        # TODO: figure out if theres a way to automatically skip this test if
        # test_constructor_does_not_error_1 fails (since this test is a
        # superset of that test)
        t = simplex.Tableau(
            inequalities=[
                simplex.Inequality([simplex.Variable("x", 1), simplex.Variable("y", 1), simplex.Variable("z", 1)], 10),
                simplex.Inequality([simplex.Variable("x", 2), simplex.Variable("y", -1)], 0),
                simplex.Inequality([simplex.Variable("x", 1), simplex.Variable("y", 3), simplex.Variable("z", -1)], -6),
                simplex.ObjectiveEquation([simplex.Variable("x", -5), simplex.Variable("y", 3), simplex.Variable("z", -4)], 0, 1)
            ]
        )
        # see test_solve_and_report_values_0 comments
        self.assertCountEqual(
            t.get_variable_values(),
            [
                (NamedTypeTag(VariableType.NORMAL, 'x'), 0),
                (NamedTypeTag(VariableType.NORMAL, 'y'), 0),
                (NamedTypeTag(VariableType.NORMAL, 'z'), 0),
                (NamedTypeTag(VariableType.SLACK, 0), 10),
                (NamedTypeTag(VariableType.SLACK, 1), 0),
                (NamedTypeTag(VariableType.SLACK, 2), -6),
                (AnonymousTypeTag(VariableType.OBJECTIVE), 0),
            ]
        )

    def test_solve_and_report_values_0(self):
        # actually just me doing further maths discrete classwork
        # but i found some bugs in my new constructor so it was useful
        # i was then able to turn this into an actual test using the new
        # constructor and value reporting function
        # print("test_temp")

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
