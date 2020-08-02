import pytest

from common.dal import EventStore


@pytest.mark.asyncio
async def test_event_store(connection, events, event_schema, aggregate_id):
    event_store = EventStore(connection, event_schema)
    data = await event_store.get(aggregate_id)
    connection.cursor.assert_called_once()
    assert data == events
    await event_store.add(data)
    connection.execute.assert_called_once()
