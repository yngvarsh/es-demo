from dataclasses import dataclass
from functools import singledispatchmethod
from typing import Awaitable, Tuple

from common.aggregate import AggregateRoot, attribute, command
from common.events import Event, EventSchema


@dataclass(frozen=True)
class First(Event):
    some_field: str


@dataclass(frozen=True)
class Second(Event):
    another_field: str


EventSchema.register(First)
EventSchema.register(Second)


class FirstAggregate(AggregateRoot):
    @attribute
    def some_field(self):
        return self.state.get("some_field", [])

    @attribute
    def another_field(self):
        return self.state.get("another_field", None)

    @singledispatchmethod
    def apply_event(self, event) -> None:
        raise NotImplementedError

    @apply_event.register
    def _(self, event: First) -> None:
        self.state.setdefault("some_field", []).append(event.some_field)

    @apply_event.register
    def _(self, event: Second) -> None:
        self.state["another_field"] = event.another_field

    def _add_some_field(self, some_field):
        return First.factory(aggregate_id=self.id, aggregate_version=self.version, some_field=some_field)

    @command
    async def add_some_field(self, some_field: str) -> First:
        return self._add_some_field(some_field)

    @command
    async def no_effect(self, some_field: str) -> None:
        pass

    @command
    async def add_some_field_with_action(self, some_field: str) -> Tuple[First, Awaitable]:
        async def effect():
            print("Effect")

        return self._add_some_field(some_field), effect()

    @command(lazy=False)
    async def add_some_field_eager(self, some_field: str) -> First:
        return self._add_some_field(some_field)
