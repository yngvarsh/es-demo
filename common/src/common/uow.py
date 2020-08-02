from contextlib import AsyncExitStack
from typing import Optional, Type

from aioredis import Redis
from asyncpgsa.transactionmanager import ConnectionTransactionContextManager

from .dal import EventStore
from .events import EventSchema
from .typing import ID, A


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

    async def aggregate_factory(self, aggregate_type: Type[A], aggregate_id: ID) -> A:
        assert self._event_store, "Event store instance wasn't created"
        events = await self._event_store.get(aggregate_id)
        return aggregate_type(aggregate_id, self._event_stack, *events)

    async def publish_events(self):
        for event in self._event_stack:
            await self._event_bus.publish(event.__class__.__name__, self._event_bus_schema.dumps(event))

    async def store_events(self):
        await self._event_store.add(self._event_stack)

    async def __aenter__(self):
        await self._stack.__aenter__()
        self._stack.push_async_callback(self.publish_events)
        self._stack.push_async_callback(self.store_events)
        connection = await self._stack.enter_async_context(self._transaction)
        self._event_store = EventStore(connection, self._event_store_schema)
        return self

    async def __aexit__(self, *args):
        return await self._stack.__aexit__(*args)
