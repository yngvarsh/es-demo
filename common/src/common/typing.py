from datetime import datetime
from typing import TYPE_CHECKING, NewType, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from .events.base import Event  # noqa: F401

ID = NewType("ID", UUID)
CreatedAt = NewType("CreatedAt", datetime)
Version = NewType("Version", int)
E = TypeVar("E", bound="Event")
