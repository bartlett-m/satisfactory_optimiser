import logging
from fractions import Fraction
from itertools import filterfalse
from utils.exceptions import AlgorithmDoneException

toplevel_logger = logging.getLogger(__name__)


class SimplexAlgorithmDoneException(AlgorithmDoneException):
    """Exception raised when the simplex algorithm completes"""
    def __init__(self):
        super(SimplexAlgorithmDoneException, self).__init__(
            "Simplex algorithm done"
        )


class TableauRow():
    def __init__(self, row: list[Fraction]) -> None:
        self._row = row

    def __mul__(self, other: object) -> type["TableauRow"]:
        return TableauRow(
            [
                coefficient * other
                for coefficient
                in self._row
            ]
        )

    def __rmul__(self, other: object) -> type["TableauRow"]:
        return TableauRow(
            [
                other * coefficient
                for coefficient
                in self._row
            ]
        )

    def __add__(self, other: type["TableauRow"]) -> type["TableauRow"]:
        if not issubclass(type(other), TableauRow):
            return NotImplemented
        return TableauRow(
            [
                coefficient_1 + coefficient_2
                for coefficient_1, coefficient_2
                in zip(
                    self._row,
                    other._row
                )
            ]
        )

    def __truediv__(self, other: object) -> type["TableauRow"]:
        return TableauRow(
            [
                coefficient / other
                for coefficient
                in self._row
            ]
        )

    def __rtruediv__(self, other: object) -> type["TableauRow"]:
        return TableauRow(
            [
                other / coefficient
                for coefficient
                in self._row
            ]
        )

    def __sub__(self, other: type["TableauRow"]) -> type["TableauRow"]:
        if not issubclass(type(other), TableauRow):
            return NotImplemented
        return self.__add__(other*-1)

    def __repr__(self) -> str:
        return self._row.__repr__()

    def __str__(self) -> str:
        return self._row.__str__()

    def min(self):
        return min(self._row)

    def index(self, item):
        return self._row.index(item)


class Tableau():
    def __init__(self) -> None:
        # TODO: this temporary jank needs to be replaced
        # with an actual constructor.
        self._tableau = [
            TableauRow([Fraction(coef) for coef in row])
            for row
            in [
                # a, b, s_1, s_2, P, RHS
                [1, 1, 1, 0, 0, 40],
                [4, 1, 0, 1, 0, 100],
                [-20, -10, 0, 0, 1, 0]  # objective row
            ]
        ]

    def _get_pivot_column(self) -> int:
        # get the objective row and find the value of the most negative entry
        most_neg = self._tableau[-1].min()
        # if there are no negative entries in the objective row, then the
        # algorithm is complete
        if most_neg >= 0:
            raise SimplexAlgorithmDoneException()
        # otherwise, get the index of this value.  this is the pivot column.
        return self._tableau[-1].index(most_neg)
        # note that the algorithm will work with any negative entry in the
        # objective row, however it is more optimal to use the most negative
        # entry.

    def _get_pivot_row(self, pivot_column: int) -> int:
        row_ratios: list[Fraction] = [
            row._row[-1] / row._row[pivot_column]
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
        element = pivoted_row._row[column]
        # divide each entry in the pivot row by the pivot element
        # NOTE: This means that the "element" variable CANNOT be used in the
        # coming lambda function since it is now out of date!
        pivoted_row = pivoted_row/element
        # make the entry in the pivot column zero for every other row
        self._tableau = list(map(
            # strip out the index variable we no longer need, then subtract
            # the pivoted row from each other row to make the entry in the
            # pivot column equal to zero for these rows
            lambda indexed_row: (
                indexed_row[1] - (
                    pivoted_row * (
                        indexed_row[1]._row[column] / pivoted_row._row[column]
                    )
                )
            ),
            # get every other row
            filterfalse(
                lambda indexed_row: indexed_row[0] == row,
                enumerate(self._tableau)
            )
        ))
        self._tableau.insert(row, pivoted_row)


# testing
def __test() -> None:
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
