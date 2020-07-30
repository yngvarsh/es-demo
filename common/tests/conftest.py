from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Tuple
from uuid import uuid4

import pytest

from common.aggregate import AggregateRoot, attribute, command
from common.events import Event


@pytest.fixture
def now():
    return datetime(2020, 8, 9, 20)


@pytest.fixture
def aggregate_id():
    return uuid4()


@pytest.fixture
def dummy_event_cls():
    @dataclass(frozen=True)
    class Dummy(Event):
        some_field: str
        current_version = 2

    return Dummy


@pytest.fixture
def dummy_aggregate_cls(dummy_event_cls):
    class DummyAggregate(AggregateRoot):
        @attribute
        def some_field(self):
            return self.state.get("some_field", [])

        def apply_event(self, event: dummy_event_cls) -> None:
            self.state.setdefault("some_field", []).append(event.some_field)

        def _add_some_field(self, some_field):
            return dummy_event_cls.factory(aggregate_id=self.id, aggregate_version=self.version, some_field=some_field)

        @command
        async def add_some_field(self, some_field: str) -> dummy_event_cls:
            return self._add_some_field(some_field)

        @command
        async def no_effect(self, some_field: str) -> None:
            pass

        @command
        async def add_some_field_with_action(self, some_field: str) -> Tuple[dummy_event_cls, Awaitable]:
            async def effect():
                print("Effect")

            return self._add_some_field(some_field), effect()

        @command(lazy=False)
        async def add_some_field_eager(self, some_field: str) -> dummy_event_cls:
            return self._add_some_field(some_field)

    return DummyAggregate
