from datetime import datetime
from typing import NewType, TypeVar
from uuid import UUID

ID = NewType("ID", UUID)
CreatedAt = NewType("CreatedAt", datetime)
Version = NewType("Version", int)

E = TypeVar("E", bound="Event")  # noqa: F821
