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
