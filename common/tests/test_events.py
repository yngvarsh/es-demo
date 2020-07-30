import pytest

from common.events import deserialize, serialize
from common.exceptions import EventVersionMismatch, InvalidSerializedEvent, UnregisteredEvent


@pytest.mark.freeze_time("2020-08-09T20:00:00")
def test_factory(event_subclass, now, aggregate_id):
    new_event = event_subclass.factory(aggregate_id=aggregate_id, some_field="abc")
    assert new_event.meta.created_at == now
    assert new_event.meta.aggregate_version == 1


def test_serde_ok(event_subclass, aggregate_id):
    new_event = event_subclass.factory(aggregate_id=aggregate_id, some_field="abc")
    serialized = serialize(new_event)
    deserialized = deserialize(serialized)
    assert new_event.meta == deserialized.meta


@pytest.mark.freeze_time("2020-08-09T20:00:00")
@pytest.mark.parametrize(
    "err,data,meta",
    [
        (InvalidSerializedEvent, {"some_field": "abc"}, {"event_version": 2, "aggregate_version": 1}),
        (InvalidSerializedEvent, {"some_field": "abc"}, {"type": "Dummy", "event_version": 2}),
        (
            InvalidSerializedEvent,
            {"another_field": "abc"},
            {"type": "Dummy", "event_version": 2, "aggregate_version": 1},
        ),
        (
            InvalidSerializedEvent,
            {"some_field": "abc", "extra_info": "Shouldn't be there"},
            {"type": "Dummy", "event_version": 2, "aggregate_version": 1},
        ),
        (UnregisteredEvent, {"some_field": "abc"}, {"type": "NotDummy", "event_version": 2, "aggregate_version": 1}),
        (EventVersionMismatch, {"some_field": "abc"}, {"type": "Dummy", "event_version": 1, "aggregate_version": 1}),
    ],
)
def test_deserialize_err(err, data, meta, now, aggregate_id):
    serialized = {"data": data, "meta": dict(meta, aggregate_id=aggregate_id, created_at=now)}
    with pytest.raises(err):
        deserialize(serialized)
