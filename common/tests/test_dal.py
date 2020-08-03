import pytest

from common.dal import add_events, get_events


@pytest.mark.asyncio
async def test_event_store(connection, events, event_schema, aggregate_id):
    data = await get_events(connection, aggregate_id)
    connection.cursor.assert_called_once()
    assert data == events
    await add_events(connection, data)
    connection.execute.assert_called_once()
