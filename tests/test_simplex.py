import unittest
from fractions import Fraction
from optimisationsolver import simplex


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
