from typing import List, Optional

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


async def get_events(connection: Connection, aggregate_id: ID, schema: Optional[EventSchema] = None) -> List[Event]:
    query = (
        stored_events.select()
        .where(stored_events.c.aggregate_id == aggregate_id)
        .order_by(stored_events.c.aggregate_version)
    )
    return [(schema or EventSchema()).loads(row["state"]) async for row in connection.cursor(query)]


async def add_events(connection: Connection, events: List[Event], schema: Optional[EventSchema] = None) -> None:
    query = stored_events.insert().values(
        [
            {
                "state": (serialized := (schema or EventSchema()).dump(event)),
                "initial": serialized,
                "aggregate_id": event.aggregate_id,
                "aggregate_version": event.aggregate_version,
                "created_at": event.created_at,
            }
            for event in events
        ]
    )
    await connection.execute(query)
