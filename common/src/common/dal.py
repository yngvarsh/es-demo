from typing import List

from asyncpg import Connection
from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON, UUID

from .events import Event, EventSchema
from .typing import ID

metadata = MetaData()
stored_events = Table(
    "stored_events",
    metadata,
    Column("pk", BigInteger, primary_key=True),
    Column("aggregate_id", UUID, nullable=False),
    Column("aggregate_version", Integer, nullable=False),
    Column("state", JSON, nullable=False),
    Column("initial", JSON, nullable=False),
    Column("created_at", DateTime, nullable=False),
    UniqueConstraint("aggregate_id", "aggregate_version"),
)


class EventStore:
    def __init__(self, connection: Connection, schema: EventSchema):
        self.connection = connection
        self.schema = schema

    async def get(self, aggregate_id: ID) -> List[Event]:
        query = (
            stored_events.select()
            .where(stored_events.c.aggregate_id == aggregate_id)
            .order_by(stored_events.c.aggregate_version)
        )
        return [self.schema.loads(row["state"]) async for row in self.connection.cursor(query)]

    async def add(self, events: List[Event]) -> None:
        query = stored_events.insert().values(
            [
                {
                    "state": (serialized := self.schema.dump(event)),
                    "initial": serialized,
                    "aggregate_id": event.meta.aggregate_id,
                    "aggregate_version": event.meta.aggregate_version,
                    "created_at": event.meta.created_at,
                }
                for event in events
            ]
        )
        await self.connection.execute(query)
