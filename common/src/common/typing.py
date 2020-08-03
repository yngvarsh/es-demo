from datetime import datetime
from typing import TYPE_CHECKING, NewType, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from .aggregate import AggregateRoot  # noqa: F401
    from .events.base import Event  # noqa: F401

ID = NewType("ID", UUID)
CreatedAt = NewType("CreatedAt", datetime)
Version = NewType("Version", int)
E = TypeVar("E", bound="Event")
A = TypeVar("A", bound="Aggregate")
G = TypeVar("G", bound="Gateway")
