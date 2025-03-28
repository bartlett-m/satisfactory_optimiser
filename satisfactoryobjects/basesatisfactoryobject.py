class BaseSatisfactoryObject:
    """A base class that contains the fields common to all satisfactory data
    objects
    """
    def __init__(
        self,
        internal_class_identifier: str,
        user_facing_name: str
    ) -> None:
        self.internal_class_identifier = internal_class_identifier
        self.user_facing_name = user_facing_name

    def __eq__(self, other: object) -> bool:
        if issubclass(type(other), BaseSatisfactoryObject):
            return (
                (
                    self.internal_class_identifier
                    ==
                    other.internal_class_identifier
                )
                and
                (
                    self.user_facing_name
                    ==
                    other.user_facing_name
                )
            )
        return False

    def __hash__(self) -> int:
        # as of all commits on 2024-12-30 before 13:45, __hash__(self)
        # implementations on any file in the satisfactoryobjects module
        # (including this one) were written using the help of
        # https://docs.python.org/3/reference/datamodel.html#object.__hash__
        # [accessed 2024-12-30 at 13:02]
        return (
            self.internal_class_identifier.__hash__()
            ^
            self.user_facing_name.__hash__()
        )
