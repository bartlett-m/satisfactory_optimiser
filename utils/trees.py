"""Tree data structures"""

from abc import ABC, abstractmethod
from typing import Type


class AbstractNode(ABC):
    def __init__(self, value):
        self._value = value

    @property
    @abstractmethod
    def children(self):
        pass

    @property
    def value(self):
        return self._value


class GenericTreeNode(AbstractNode):
    def __init__(
        self,
        value,
        children: list[Type["GenericTreeNode"]] | None
    ) -> None:
        super().__init__(value)
        self._children = children

    @property
    def children(self):
        return self._children


class BinaryTreeNode(AbstractNode):
    def __init__(
        self,
        value,
        left: Type["BinaryTreeNode"] | None,
        right: Type["BinaryTreeNode"] | None
    ) -> None:
        super().__init__(value)
        self.left = left
        self.right = right

    @property
    def children(self):
        if self.left is None and self.right is None:
            return None
        else:
            _ret = list()
            for possible_child in [self.left, self.right]:
                if possible_child is not None:
                    _ret.append(possible_child)
            return _ret
