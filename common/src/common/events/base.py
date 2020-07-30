from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import ClassVar, Dict, Optional, Type

from ..typing import ID, CreatedAt, E, Version

_REGISTRY: Dict[str, Type[Event]] = {}
REGISTRY = MappingProxyType(_REGISTRY)


@dataclass(frozen=True)
class EventMeta:
    aggregate_id: ID
    aggregate_version: Version
    event_version: Version
    created_at: CreatedAt


@dataclass(frozen=True)
class Event:
    meta: EventMeta
    current_version: ClassVar[Version] = 1

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _REGISTRY.setdefault(cls.__name__, cls)

    @classmethod
    def factory(
        cls: Type[E], aggregate_id: ID, aggregate_version: Version = 1, created_at: Optional[CreatedAt] = None, **data,
    ) -> E:
        return cls(
            meta=EventMeta(
                aggregate_id=aggregate_id,
                aggregate_version=aggregate_version,
                event_version=cls.current_version,
                created_at=created_at or datetime.utcnow(),
            ),
            **data,
        )
