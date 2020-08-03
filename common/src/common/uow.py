from contextlib import AsyncExitStack, asynccontextmanager

from aioredis import Redis
from asyncpgsa.transactionmanager import ConnectionTransactionContextManager

from .dal import add_events
from .events import EventSchema


class UnitOfWork:
    def __init__(
        self,
        transaction: ConnectionTransactionContextManager,
        redis: Redis,
        event_store_schema: EventSchema,
        event_bus_schema: EventSchema,
    ):
        self._transaction = transaction
        self._event_bus = redis
        self._stack = AsyncExitStack()
        self._event_store_schema = event_store_schema
        self._event_bus_schema = event_bus_schema
        self.event_stack = []
        self.connection = None

    @asynccontextmanager
    async def publish_events(self):
        yield
        for event in self.event_stack:
            await self._event_bus.publish(event.__class__.__name__, self._event_bus_schema.dumps(event))

    @asynccontextmanager
    async def store_events(self):
        yield
        if self.event_stack:
            await add_events(self.connection, self.event_stack, schema=self._event_store_schema)

    async def __aenter__(self):
        await self._stack.__aenter__()
        self.connection = await self._stack.enter_async_context(self._transaction)
        await self._stack.enter_async_context(self.publish_events())
        await self._stack.enter_async_context(self.store_events())
        return self

    async def __aexit__(self, *args):
        return await self._stack.__aexit__(*args)
