import pytest

from .fake import FirstAggregate


@pytest.mark.asyncio
async def test_aggregate_new(capsys):
    aggregate = FirstAggregate()
    assert aggregate.version == 0
    assert aggregate.some_field == []
    await aggregate.add_some_field("foo")
    await aggregate.add_some_field("bar")
    assert len(aggregate.internal) == 1
    assert len(aggregate.event_stack) == 2
    await aggregate.add_some_field_with_action("baz")
    assert len(aggregate.actions) == 1
    await aggregate.no_effect("qwe")
    await aggregate.add_some_field_eager("qwe")
    assert capsys.readouterr().out == "Effect\n"
    assert len(aggregate.internal) == 0
    assert aggregate.some_field == ["foo", "bar", "baz", "qwe"]
    assert aggregate.version == 4
    assert len(aggregate.event_stack) == 4


@pytest.mark.asyncio
async def test_aggregate_from_events(events, aggregate_id):
    aggregate = FirstAggregate(aggregate_id, [], *events)
    assert aggregate.some_field == ["foo", "bar", "baz"]
    assert aggregate.another_field == "two"
