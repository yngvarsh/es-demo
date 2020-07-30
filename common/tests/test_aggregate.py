import pytest


@pytest.mark.asyncio
async def test_aggregate(dummy_aggregate_cls, aggregate_id, capsys):
    aggregate = dummy_aggregate_cls(id=aggregate_id, queue=[])
    assert aggregate.version == 0
    assert aggregate.some_field == []
    await aggregate.add_some_field("foo")
    await aggregate.add_some_field("bar")
    assert len(aggregate.events) == 1
    assert len(aggregate.queue) == 1
    await aggregate.add_some_field_with_action("baz")
    assert len(aggregate.actions) == 1
    await aggregate.no_effect("qwe")
    assert len(aggregate.queue) == 3
    await aggregate.add_some_field_eager("qwe")
    assert capsys.readouterr().out == "Effect\n"
    assert len(aggregate.events) == 0
    assert len(aggregate.queue) == 4
    assert aggregate.some_field == ["foo", "bar", "baz", "qwe"]
    assert aggregate.version == 4
