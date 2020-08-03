from contextlib import AsyncExitStack, asynccontextmanager
from typing import Optional, Type

from aioredis import Redis
from asyncpgsa.transactionmanager import ConnectionTransactionContextManager

from .dal import EventStore
from .events import EventSchema
from .typing import ID, A, G


class UnitOfWork:
    def __init__(
        self,
        transaction: ConnectionTransactionContextManager,
        redis: Redis,
        event_store_schema: EventSchema,
        event_bus_schema: EventSchema,
    ):
        self._transaction = transaction
        self._event_store: Optional[EventStore] = None
        self._event_bus = redis
        self._stack = AsyncExitStack()
        self._event_store_schema = event_store_schema
        self._event_bus_schema = event_bus_schema
        self._event_stack = []
        self.connection = None

    async def aggregate_factory(
        self, aggregate_type: Type[A], aggregate_id: Optional[ID] = None, *, gateway_cls: Optional[Type[G]] = None
    ) -> A:
        assert self._event_store, "Event store instance wasn't created"
        events = await self._event_store.get(aggregate_id) if aggregate_id else ()
        return aggregate_type(
            aggregate_id, self._event_stack, *events, gateway=gateway_cls(self.connection) if gateway_cls else None
        )

    @asynccontextmanager
    async def publish_events(self):
        yield
        for event in self._event_stack:
            await self._event_bus.publish(event.__class__.__name__, self._event_bus_schema.dumps(event))

    @asynccontextmanager
    async def store_events(self):
        yield
        if self._event_stack:
            await self._event_store.add(self._event_stack)

    async def __aenter__(self):
        await self._stack.__aenter__()
        self.connection = await self._stack.enter_async_context(self._transaction)
        await self._stack.enter_async_context(self.publish_events())
        await self._stack.enter_async_context(self.store_events())
        self._event_store = EventStore(self.connection, self._event_store_schema)
        return self

    async def __aexit__(self, *args):
        return await self._stack.__aexit__(*args)
