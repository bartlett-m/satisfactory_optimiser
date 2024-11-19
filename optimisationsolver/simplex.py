import logging
from numbers import Rational
from fractions import Fraction
from typing import Iterable
from itertools import filterfalse, repeat, chain
from utils.exceptions import AlgorithmDoneException

toplevel_logger = logging.getLogger(__name__)


class SimplexAlgorithmDoneException(AlgorithmDoneException):
    """Exception raised when the simplex algorithm completes"""
    def __init__(self):
        super(SimplexAlgorithmDoneException, self).__init__(
            "Simplex algorithm done"
        )


# helper utility that handles the special case of division by zero in the
# simplex algorithm
def pivot_div(numerator: Rational, denominator: Rational) -> Fraction | None:
    # TODO: return a different result for positive value divided by zero and
    # negative value divided by zero
    # a negative value divided by zero should (iirc) be skipped, a positive
    # value divided by zero should be preferred (or it might be the other way
    # round)
    try:
        # TODO: remove try-except and instead repurpose this new guard clause
        # we dont care about what the ratio would be if it is less than zero
        # anyway, so we can just not bother for those cases and return None
        if numerator == 0 and denominator <= 0:
            return None
        return Fraction(numerator, denominator)
    except ZeroDivisionError:
        # In this case, we want to ignore this row.  One possible solution
        # would be to return a special type here that signifies a division by
        # zero.  Another solution would be to return positive infinity,
        # however this would make troubleshooting harder if for whatever
        # reason every row ratio check resulted in a division by zero.  A
        # third (hacky) solution is to rely on the fact that we are already
        # filtering out negative ratios, and just return Fraction(-1).
        #
        # For the sake of my own sanity, I will be modifying my type hints to
        # additionaly permit a a return of None (as opposed to a raised
        # ZeroDivsionError), and then I will check for that in my filter
        return None


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

    def __eq__(self, other: object) -> bool:
        if issubclass(type(other), TableauRow):
            return self._row == other._row
        return self._row == other

    def __repr__(self) -> str:
        return self._row.__repr__()

    def __str__(self) -> str:
        return self._row.__str__()

    def min(self):
        return min(self._row)

    def index(self, item):
        return self._row.index(item)

    def _get_rhs(self) -> Fraction:
        return self._row[-1]

    rhs = property(
        fget=_get_rhs,
        doc="The value of the right-hand-side of this row"
    )


# for backwards compatibility with old debug code
_temp_debug_tableau = [
    TableauRow([Fraction(coef) for coef in row])
    for row
    in [
        # a, b, s_1, s_2, P, RHS
        [1, 1, 1, 0, 0, 40],
        [4, 1, 0, 1, 0, 100],
        [-20, -10, 0, 0, 1, 0]  # objective row
    ]
]


class Variable():
    # TODO: this would probably make way more sense as a named tuple?
    def __init__(
        self,
        id,
        coefficient: Rational,
    ):
        self.id = id
        self.coefficient = coefficient

    def __iter__(self):
        # to allow unpacking
        # see https://stackoverflow.com/a/37837754
        return iter((self.id, self.coefficient))


class Inequality():
    def __init__(
        self,
        lhs: Iterable[Variable],
        rhs: Rational
    ):
        self._lhs = {
            var.id: var.coefficient
            for var
            in lhs
        }  # make this a dictionary of variable_id:coefficient and other data
        # see comment in tableau_left_padded about casting to fraction
        self.rhs = Fraction(rhs)

    def _get_lhs(self):
        return [Variable(_id, coef) for _id, coef in self._lhs.items()]

    lhs = property(
        fget=_get_lhs,
        doc="The left hand side of the inequality (minus the \
            objective variable), as a list of variables"
    )

    def _get_obj_coef(self) -> Rational:
        return Fraction(0)

    objective_coefficient = property(
        fget=_get_obj_coef,
        doc="The coefficient of the objective variable"
    )

    def tableau_left_padded(self, _vars: list[Variable]):

        for variable_id in _vars:
            # this isnt all executed at once (it is paused after each yield
            # until the next item is requested)
            try:
                variable_coef = self._lhs[variable_id]
                # cast to fraction here to ensure that when the actual tableau
                # gets pivoted then the fraction division implementation is
                # used instead of the integer division implementation, which
                # would return floats which are imprecise and also cannot be
                # used in the pivot_div function to construct fractions, since
                # float does not subclass rational.
                yield Fraction(variable_coef)
            except KeyError:
                # no such variable in this inequality
                yield Fraction(0)


class ObjectiveEquation(Inequality):
    def __init__(
        self,
        lhs: Iterable[Variable],
        rhs: Rational,
        objective_coefficient: Rational
    ):
        super().__init__(lhs, rhs)
        self._objective_coefficient = objective_coefficient

    def _get_obj_coef(self) -> Rational:
        return Fraction(self._objective_coefficient)

    objective_coefficient = property(
        fget=_get_obj_coef,
        doc="The coefficient of the objective variable"
    )


class Tableau():
    def __init__(
        self,
        tableau: list[TableauRow] = _temp_debug_tableau,
        inequalities: list[Inequality] = [],
    ) -> None:
        if inequalities == []:
            # TODO: this temporary jank needs to be replaced
            # with an actual constructor.
            self._tableau = tableau
            # legacy constructor used in some tests.
            # it is entirely ignored if the inequalities argument is set.
            # to do so, the tableau argument can be left as the default
            # and the inequalities argument is set by its keyword.
            # this legacy parameter will eventually be removed
        else:
            self._tableau: list[list[Fraction]] = []
            _vars = set()
            for inequality in inequalities:
                for variable_id in inequality._lhs:
                    # inequality._lhs is the internal dictionary
                    # representation of the inequality.
                    # since we only care about the keys (variable ids) it is
                    # quicker to just iterate through the keys directly,
                    # since this does not involve initialising new Variable
                    # objects.
                    _vars.add(variable_id)

            _sorted_vars = list(_vars)
            # to prevent fun bugs when the order of variables isnt consistent
            # throughout the tableau
            # python sets are sorted from my experience, but considering how long
            # i have spent debugging this file in particular i dont want to take
            # chances
            _sorted_vars.sort()

            self._tableau_header: list = list(
                chain.from_iterable(
                    [
                        _sorted_vars,
                        # TODO: use a custom type for variable ids to differentiate slack variables etc
                        [f"s_{i}" for i in range(len(inequalities))],
                        ["I", "RHS"]
                    ]
                )
            )

            for inequality_idx, inequality in enumerate(inequalities):
                # cast to list to immediately evaluate the iterable
                _row = list(
                    # itertools chain to stitch various iterables for
                    # different parts of the tableau together
                    chain.from_iterable(
                        [
                            # this function returns an iterable that returns
                            # all the left side of the tableau, with any
                            # variables that dont exist being set to zero
                            inequality.tableau_left_padded(_sorted_vars),
                            # filler zeroes for slack variables
                            repeat(Fraction(0), inequality_idx),
                            # for slack variable (do not include for the
                            # objective row)
                            (
                                []
                                if issubclass(
                                    type(inequality),
                                    ObjectiveEquation
                                )
                                else [Fraction(1)]
                            ),
                            # remaining zeroes for slack variables
                            # (max ensures that there isnt -1 or -2 repeats
                            # for the objective row)
                            repeat(
                                Fraction(0),
                                max([
                                    (len(inequalities) - (inequality_idx + 2)),
                                    0
                                ])
                            ),
                            # objective coefficient and right-hand-side of the
                            # inequality
                            [inequality.objective_coefficient, inequality.rhs]
                        ]
                    )
                )
                self._tableau.append(TableauRow(_row))

    def _get_pivot_column(self) -> int:
        # # get the objective row and find the value of the most negative entry
        # most_neg = self._tableau[-1].min()
        # # if there are no negative entries in the objective row, then the
        # # algorithm is complete
        # if most_neg >= 0:
        #     raise SimplexAlgorithmDoneException()
        # # otherwise, get the index of this value.  this is the pivot column.
        # return self._tableau[-1].index(most_neg)
        # # note that the algorithm will work with any negative entry in the
        # # objective row, however it is more optimal to use the most negative
        # # entry.

        # hacky patch to try and make it not cycle by using blands rule
        for column, entry in enumerate(self._tableau[-1]._row):
            if entry < 0:
                return column
        raise SimplexAlgorithmDoneException()

    def _get_pivot_row(self, pivot_column: int) -> int:
        row_ratios: list[Fraction | None] = [
            pivot_div(row._row[-1], row._row[pivot_column])
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
                    lambda ratio: ratio is None or ratio < 0,
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

    def pivot_until_done(self) -> None:
        try:
            while True:
                self.pivot()
        except SimplexAlgorithmDoneException:
            return  # done now

    def _get_variable_value(self, column: int) -> Fraction:
        # if the variable is basic, its column has all zeroes except for a
        # single row with a value of one.  the right hand side of the row with
        # a one is the value of this basic variable.  otherwise, the variable
        # is non-basic and always has a value of zero.

        # note that this will run on the right-hand-side without complaint,
        # even though that operation doesnt make sense from a practical
        # standpoint
        possible_value = None
        for row in self._tableau:
            if (
                (
                    not (
                        row._row[column] == 0
                        or
                        row._row[column] == 1
                    )
                )
                or
                (
                    row._row[column] == 1
                    and
                    possible_value is not None
                )
            ):
                return Fraction(0)
            elif row._row[column] == 1:
                possible_value = row.rhs
        return (Fraction(0) if possible_value is None else possible_value)

    def get_variable_values(self) -> list:  # TODO: more specific type hint
        _ret: list = [
            (var_id, self._get_variable_value(idx))
            for idx, var_id
            # remember to strip out right-hand-side!
            in enumerate(self._tableau_header[:-1])
        ]

        return _ret
