"""
This module contains single dispatch registries for events serialization and deserialization with default
implementations. Concrete implementations are expected to be registered in services.
"""

from dataclasses import asdict
from functools import singledispatch

from ..exceptions import EventVersionMismatch, InvalidSerializedEvent, UnregisteredEvent
from .base import REGISTRY, Event, EventMeta


@singledispatch
def serialize(event: Event) -> dict:
    """Default event serializer"""
    data = asdict(event)
    meta = data.pop("meta")
    meta["type"] = event.__class__.__name__
    return {"data": data, "meta": meta}


@singledispatch
def deserialize(event: dict) -> Event:
    """Default event deserializer"""
    try:
        if not (cls := REGISTRY.get(clsname := event["meta"]["type"])):
            raise UnregisteredEvent(clsname)
        elif (current_version := cls.current_version) != (event_version := event["meta"]["event_version"]):
            raise EventVersionMismatch(clsname, current_version, event_version)
        else:
            return cls(
                meta=EventMeta(
                    aggregate_id=event["meta"]["aggregate_id"],
                    aggregate_version=event["meta"]["aggregate_version"],
                    event_version=event_version,
                    created_at=event["meta"]["created_at"],
                ),
                **event["data"],  # type: ignore
            )
    except (TypeError, KeyError):
        raise InvalidSerializedEvent
