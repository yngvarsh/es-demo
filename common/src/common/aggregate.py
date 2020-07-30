from abc import ABC, abstractmethod
from collections import deque
from functools import partial, wraps
from typing import Awaitable, Callable, Deque, List, NamedTuple, Optional, Tuple, Union

from .events import Event
from .typing import ID, Version


class EventWrapper(NamedTuple):
    event: Event
    processed: bool


class AggregateRoot(ABC):
    def __init__(self, queue: List[Event], id: Optional[ID] = None):
        self.id = id
        self.queue = queue
        self.version = Version(0)
        self.state: dict = {}
        self.events: Deque[EventWrapper] = deque()
        self.actions: Deque[Awaitable] = deque()

    def apply_all_events(self) -> None:
        while len(self.events) > 0:
            event, processed = self.events.popleft()
            self.apply_event(event)
            self.version += Version(1)
            if not processed:
                self.queue.append(event)

    async def apply_all_actions(self) -> None:
        while len(self.actions) > 0:
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
            aggregate.events.append(EventWrapper(event, processed=False))
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
