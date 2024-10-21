"""Enums to represent the type of variable in linear programming equations"""

from enum import Enum, IntFlag
# imported using "as" to prevent a name conflict with the operator property of
# the InequalityTypeEnum
import operator as python_builtin_operator


class VariableType(Enum):
    NORMAL = 1
    SLACK = 2
    CONSTANT = 3
    OBJECTIVE = 4


class InequalityTypeEnum(IntFlag):
    # the base flags
    EQUAL = 2**0
    GREATER_THAN = 2**1
    LESS_THAN = 2**2
    # combinations of those flags that represent other common inequality types
    GREATER_THAN_OR_EQUAL = GREATER_THAN | EQUAL
    LESS_THAN_OR_EQUAL = LESS_THAN | EQUAL
    # not equal is also valid but has fewer practical uses
    # including it for completeness
    NOT_EQUAL = GREATER_THAN | LESS_THAN
    # these are technically valid but I cant see what you would use them for
    # please enlighten me if you can think of a practical use for such
    # combinations of flags
    ANY = GREATER_THAN | LESS_THAN | EQUAL
    NONE = 0

    @property
    def operator(self):
        """Returns the operator function corresponding to the enum flags"""
        if self._value_ == 2**0:
            return python_builtin_operator.eq
        elif self._value_ == 2**1:
            return python_builtin_operator.gt
        elif self._value_ == 2**2:
            return python_builtin_operator.lt
        elif self._value_ == 2**0 | 2**1:
            return python_builtin_operator.ge
        elif self._value_ == 2**0 | 2**2:
            return python_builtin_operator.le
        elif self._value_ == 2**1 | 2**2:
            return python_builtin_operator.ne
        elif self._value_ == 0:
            return lambda _l, _r: False
        elif self._value_ == 2**0 | 2**1 | 2**2:
            return lambda _l, _r: True
        else:
            # The enum will never have any other bit configuration than those
            # checked for above unless modified without using bit operators
            # and the enum values.
            # If such a configuration arises, then the enum does not represent
            # a valid inequality that has a corresponding operator.  Therefore,
            # we throw an exception rather than permitting undefined behaviour.
            raise ValueError(
                "Enum bitmask {0:b} corrupt for a InequalityTypeEnum".format(
                    self._value_
                )
            )
