"""A selection of utility classes for working with queues

PrioritisedItem is from the official Python documentation, with
minor modification (british spelling + docstring). See
https://docs.python.org/3/library/queue.html#queue.PriorityQueue
for original implementation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PrioritisedItem:
    """An item with a priority, for use in a priority queue"""
    priority: int
    item: Any = field(compare=False)
