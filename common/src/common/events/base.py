from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Dict, Optional, Type
from uuid import uuid4

from ..typing import ID, CreatedAt, E, Version

_REGISTRY: Dict[str, Type["Event"]] = {}
REGISTRY = MappingProxyType(_REGISTRY)


@dataclass(frozen=True)
class EventMeta:
    aggregate_id: ID
    aggregate_version: Version
    created_at: CreatedAt


@dataclass(frozen=True)
class Event:
    meta: EventMeta

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _REGISTRY.setdefault(cls.__name__, cls)

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
