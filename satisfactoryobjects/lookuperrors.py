"""Errors raised when looking up satisfactory objects fails"""


class BaseSatisfactoryObjectLookupError(LookupError):
    pass


class ItemLookupError(BaseSatisfactoryObjectLookupError):
    pass


class MachineLookupError(BaseSatisfactoryObjectLookupError):
    pass


class RecipeLookupError(BaseSatisfactoryObjectLookupError):
    pass
