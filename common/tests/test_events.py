import pytest

from marshmallow import ValidationError


@pytest.mark.freeze_time("2020-08-09T20:00:00")
def test_event(event_cls_1, now, aggregate_id):
    new_event = event_cls_1.factory(aggregate_id=aggregate_id, some_field="abc")
    assert new_event.meta.created_at == now
    assert new_event.meta.aggregate_version == 0
    same_event = event_cls_1.factory(aggregate_id=aggregate_id, aggregate_version=0, some_field="abc")
    assert new_event == same_event
    next_event = event_cls_1.factory(aggregate_id=aggregate_id, aggregate_version=1, some_field="abc")
    assert new_event != next_event
    assert next_event > new_event


def test_serde_ok(aggregate_id, event_cls_1, event_cls_2, event_schema):
    new_event_1 = event_cls_1.factory(aggregate_id=aggregate_id, some_field="abc")
    serialized = event_schema.dump(new_event_1)
    deserialized = event_schema.load(serialized)
    assert new_event_1 == deserialized
    new_event_2 = event_cls_2.factory(aggregate_id=aggregate_id, another_field="abc")
    assert new_event_2 == event_schema.loads(event_schema.dumps(new_event_2))


@pytest.mark.freeze_time("2020-08-09T20:00:00")
@pytest.mark.parametrize(
    "data,meta",
    [
        ({"some_field": "abc"}, {"aggregate_version": 1, "created_at": "2020-08-09T20:00:00"}),
        ({"event_type": "First", "some_field": "abc"}, {"aggregate_version": 1}),
        (
            {"event_type": "First", "another_field": "abc"},
            {"aggregate_version": 1, "created_at": "2020-08-09T20:00:00"},
        ),
        (
            {"event_type": "First", "some_field": "abc", "extra_field": "abc"},
            {"aggregate_version": 1, "created_at": "2020-08-09T20:00:00"},
        ),
    ],
)
def test_deserialize_err(data, meta, aggregate_id, event_schema):
    serialized = {**data, "meta": dict(meta, aggregate_id=str(aggregate_id))}
    with pytest.raises(ValidationError):
        event_schema.load(serialized)
