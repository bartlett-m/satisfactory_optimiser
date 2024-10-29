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

    def test_solve_1(self):
        # when pivoting, this test will try a division by zero
        t = simplex.Tableau(
            [
                simplex.TableauRow([Fraction(x) for x in [1, 1, 1, 1, 0, 0, 0, 10]]),
                simplex.TableauRow([Fraction(x) for x in [2, -1, 0, 0, 1, 0, 0, 0]]),
                simplex.TableauRow([Fraction(x) for x in [-1, -3, 1, 0, 0, 1, 0, 6]]),
                simplex.TableauRow([Fraction(x) for x in [-5, 3, -4, 0, 0, 0, 1, 0]])
            ]
        )
        t.pivot_until_done()
