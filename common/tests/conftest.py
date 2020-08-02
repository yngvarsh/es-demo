from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Tuple
from uuid import uuid4

import pytest

from common.aggregate import AggregateRoot, attribute, command
from common.events import Event, EventSchema


@pytest.fixture
def now():
    return datetime(2020, 8, 9, 20)


@pytest.fixture
def aggregate_id():
    return uuid4()


@pytest.fixture
def event_cls_1():
    @dataclass(frozen=True)
    class First(Event):
        some_field: str

    return First


@pytest.fixture
def event_cls_2():
    @dataclass(frozen=True)
    class Second(Event):
        another_field: str

    return Second


@pytest.fixture
def event_schema(event_cls_1, event_cls_2):
    EventSchema.register(event_cls_1)
    EventSchema.register(event_cls_2)
    return EventSchema()


@pytest.fixture
def dummy_aggregate_cls(event_cls_1):
    class FirstAggregate(AggregateRoot):
        @attribute
        def some_field(self):
            return self.state.get("some_field", [])

        def apply_event(self, event: event_cls_1) -> None:
            self.state.setdefault("some_field", []).append(event.some_field)

        def _add_some_field(self, some_field):
            return event_cls_1.factory(aggregate_id=self.id, aggregate_version=self.version, some_field=some_field)

        @command
        async def add_some_field(self, some_field: str) -> event_cls_1:
            return self._add_some_field(some_field)

        @command
        async def no_effect(self, some_field: str) -> None:
            pass

        @command
        async def add_some_field_with_action(self, some_field: str) -> Tuple[event_cls_1, Awaitable]:
            async def effect():
                print("Effect")

            return self._add_some_field(some_field), effect()

        @command(lazy=False)
        async def add_some_field_eager(self, some_field: str) -> event_cls_1:
            return self._add_some_field(some_field)

    return FirstAggregate
