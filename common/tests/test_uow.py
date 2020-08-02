import pytest

from common.uow import UnitOfWork

from .fake import FirstAggregate


@pytest.mark.asyncio
async def test_uow(transaction, connection, redis, event_schema, aggregate_id):
    async with UnitOfWork(transaction, redis, event_schema, event_schema) as uow:
        aggregate = await uow.aggregate_factory(FirstAggregate, aggregate_id)
        assert len(aggregate.internal) == 5
        await aggregate.add_some_field_eager("abc")
        await aggregate.add_some_field("def")
        assert aggregate.some_field == ["foo", "bar", "baz", "abc", "def"]
    connection.execute.assert_called_once()
    assert redis.publish.call_count == 2
