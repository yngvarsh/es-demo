from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Dict, Optional, Type
from uuid import uuid4

from ..typing import ID, CreatedAt, E, Version

_REGISTRY: Dict[str, Type["Event"]] = {}
REGISTRY = MappingProxyType(_REGISTRY)


@dataclass(frozen=True, order=True)
class EventMeta:
    created_at: CreatedAt
    aggregate_id: ID = field(compare=True)
    aggregate_version: Version = field(compare=True)


@dataclass(frozen=True, order=False)
class Event:
    meta: EventMeta

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _REGISTRY.setdefault(cls.__name__, cls)

    def __gt__(self, other: "Event") -> bool:
        return isinstance(other, self.__class__) and self.meta > other.meta

    @classmethod
    def factory(
        cls: Type[E],
        aggregate_id: Optional[ID] = None,
        aggregate_version: Version = Version(0),  # noqa: B008
        created_at: Optional[CreatedAt] = None,
        **data,
    ) -> E:
        return cls(
            meta=EventMeta(
                aggregate_id=aggregate_id or ID(uuid4()),
                aggregate_version=aggregate_version,
                created_at=created_at or CreatedAt(datetime.utcnow()),
            ),
            **data,  # type: ignore
        )
