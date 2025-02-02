from abc import ABC, abstractmethod
from collections import deque
from functools import partial, wraps
from typing import Awaitable, Callable, Deque, List, Optional, Tuple, Union

from asyncpg import Connection

from .dal import get_events
from .events import Event
from .typing import ID, Version


class AggregateRoot(ABC):
    version = Version(0)

    def __init__(
        self,
        id: Optional[ID] = None,
        event_stack: Optional[List[Event]] = None,
        connection: Optional[Connection] = None,
        *events: Event,
    ):
        self.id = id
        self.state: dict = {}
        self.event_stack = event_stack if event_stack is not None else []
        self.connection = connection
        self.internal: Deque[Event] = deque()
        if events:
            self.internal.extend(events)
        self.actions: Deque[Awaitable] = deque()

    async def load_events(self):
        assert self.id, "User wasn't created"
        assert self.connection, "Aggregate doesn't have database connection"
        events = await get_events(self.connection, self.id)
        self.internal.extend(events)
        return self

    def __await__(self):
        return self.load_events().__await__()

    def apply_all_events(self) -> None:
        while len(self.internal):
            event = self.internal.popleft()
            self.apply_event(event)
            self.version += Version(1)

    async def apply_all_actions(self) -> None:
        while len(self.actions):
            action = self.actions.popleft()
            await action

    async def enforce(self) -> None:
        self.apply_all_events()
        await self.apply_all_actions()

    @abstractmethod
    def apply_event(self, event: Event) -> None:
        raise NotImplementedError


def command(method: Callable[..., Awaitable[Union[Event, Tuple[Event, Awaitable]]]] = None, *, lazy: bool = True):
    """
    This decorator applies all previously created events and actions for aggregate root
    and add event and optionally action produced by method to queue.
    """

    if not method:
        return partial(command, lazy=lazy)

    @wraps(method)
    async def inner(aggregate: AggregateRoot, *args, **kwargs) -> Event:
        await aggregate.enforce()
        method_rv = await method(aggregate, *args, **kwargs)
        event, action = method_rv, None
        if isinstance(method_rv, tuple):
            event, action = method_rv
        if event:
            aggregate.internal.append(event)
            aggregate.event_stack.append(event)
        if action:
            aggregate.actions.append(action)
        if not lazy:
            await aggregate.enforce()
        return event

    return inner


def attribute(getter):
    @property
    @wraps(getter)
    def inner(aggregate: AggregateRoot):
        aggregate.apply_all_events()
        return getter(aggregate)

    return inner
