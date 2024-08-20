class BaseSatisfactoryObjectLookupError(LookupError):
    pass


class ItemLookupError(BaseSatisfactoryObjectLookupError):
    pass


class MachineLookupError(BaseSatisfactoryObjectLookupError):
    pass
