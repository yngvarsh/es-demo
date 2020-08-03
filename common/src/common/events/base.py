from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Dict, Optional, Type
from uuid import uuid4

from ..typing import ID, CreatedAt, E, Version

_REGISTRY: Dict[str, Type["Event"]] = {}
REGISTRY = MappingProxyType(_REGISTRY)


@dataclass(frozen=True)
class Event:
    aggregate_id: ID
    aggregate_version: Version
    created_at: CreatedAt

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _REGISTRY.setdefault(cls.__name__, cls)

    @classmethod
    def factory(
        cls: Type[E],
        aggregate_id: Optional[ID] = None,
        aggregate_version: Optional[Version] = None,  # noqa: B008
        created_at: Optional[CreatedAt] = None,
        **data,
    ) -> E:
        return cls(
            aggregate_id=aggregate_id or ID(uuid4()),
            aggregate_version=aggregate_version if aggregate_version is not None else Version(0),
            created_at=created_at or CreatedAt(datetime.utcnow()),
            **data,  # type: ignore
        )
