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
