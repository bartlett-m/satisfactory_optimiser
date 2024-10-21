import logging
from fractions import Fraction
from itertools import filterfalse

toplevel_logger = logging.getLogger(__name__)


class Tableau():
    def __init__(self) -> None:
        self._tableau = [[Fraction(coef) for coef in row] for row in [
            # a, b, s_1, s_2, P, RHS
            [1, 1, 1, 0, 0, 40],
            [4, 1, 0, 1, 0, 100],
            [-20, -10, 0, 0, 1, 0]  # objective row
        ]]

    def _get_pivot_column(self) -> int:
        # get the objective row and find the value of the most negative entry
        most_neg = min(self._tableau[-1])
        # if there are no negative entries in the objective row, then the
        # algorithm is complete
        if most_neg >= 0:
            raise Exception("simplex done")  # TODO: use a custom exception
        # otherwise, get the index of this value.  this is the pivot column.
        return self._tableau[-1].index(most_neg)
        # note that the algorithm will work with any negative entry in the
        # objective row, however it is more optimal to use the most negative
        # entry.

    def _get_pivot_row(self, pivot_column: int) -> int:
        row_ratios: list[Fraction] = [
            row[-1] / row[pivot_column]
            for row
            # exclude the objective row via slicing
            in self._tableau[:-1]
        ]
        # the pivot row is the row with the smallest non-negative ratio
        return row_ratios.index(
            # find the smallest ratio
            min(
                # filter out the negative ratios
                filterfalse(
                    lambda ratio: ratio < 0,
                    row_ratios
                )
            )
        )

    def pivot(self) -> None:  # pivoting is in-place
        column = self._get_pivot_column()
        row = self._get_pivot_row(column)
        # get a copy of the pivot row, which will then be modified
        pivoted_row = self._tableau[row]
        # get a copy of the pivot element, which will be used to modify the
        # pivot row
        element = pivoted_row[column]
        # divide each entry in the pivot row by the pivot element
        pivoted_row = [
            entry/element
            for entry
            in pivoted_row
        ]
        # make the entry in the pivot column zero for every other row
        self._tableau = list(map(
            # strip out the index variable we no longer need, then subtract
            # the pivoted row from each other row to make the entry in the
            # pivot column equal to zero for these rows
            lambda indexed_row: [
                entry - (
                    pivoted_row[idx] * (
                        indexed_row[1][column] / pivoted_row[column]
                    )
                )
                for idx, entry
                in enumerate(indexed_row[1])
            ],
            # get every other row
            filterfalse(
                lambda indexed_row: indexed_row[0] == row,
                enumerate(self._tableau)
            )
        ))
        self._tableau.insert(row, pivoted_row)


# testing
if __name__ == "__main__":
    t = Tableau()
    for row in t._tableau:
        print(row)
    t.pivot()
    print()
    for row in t._tableau:
        print(row)
    t.pivot()
    print()
    for row in t._tableau:
        print(row)
    t.pivot()
    print()
    for row in t._tableau:
        print(row)
