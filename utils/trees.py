"""Tree data structures"""

from abc import ABC, abstractmethod
from typing import Type


class AbstractNode(ABC):
    def __init__(self, value) -> None:
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
        children: list[Type["GenericTreeNode"]] | None = None
    ) -> None:
        super().__init__(value)
        self._children = (list() if children is None else children)

    @property
    def children(self):
        return self._children


class BinaryTreeNode(AbstractNode):
    def __init__(
        self,
        value,
        left: Type["BinaryTreeNode"] | None = None,
        right: Type["BinaryTreeNode"] | None = None
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

    def add_child(self, value):
        if value < self.value:
            if self.left is None:
                self.left = BinaryTreeNode(value)
            else:
                self.left.add_child(value)
        elif value > self.value:
            if self.right is None:
                self.right = BinaryTreeNode(value)
            else:
                self.right.add_child(value)
        else:
            if self.left is None:
                self.left = BinaryTreeNode(value)
            else:
                old_left = self.left
                self.left = BinaryTreeNode(value, old_left)

    def dfs(self):
        '''CAUTION: it is inadvisable to modify the binary tree midway through using this generator'''
        if self.left is not None:
            yield from self.left.dfs()
        yield self.value
        if self.right is not None:
            yield from self.right.dfs()
