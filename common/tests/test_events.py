import pytest

from marshmallow import ValidationError

from common.typing import Version

from .fake import First, Second


@pytest.mark.freeze_time("2020-08-09T20:00:00")
def test_event(now, aggregate_id):
    new_event = First.factory(aggregate_id=aggregate_id, some_field="abc")
    assert new_event.created_at == now
    assert new_event.aggregate_version == 0
    same_event = First.factory(aggregate_id=aggregate_id, aggregate_version=Version(0), some_field="abc")
    assert new_event == same_event
    next_event = First.factory(aggregate_id=aggregate_id, aggregate_version=Version(1), some_field="abc")
    assert new_event != next_event


def test_serde_ok(aggregate_id, event_schema):
    new_event_1 = First.factory(aggregate_id=aggregate_id, some_field="abc")
    serialized = event_schema.dump(new_event_1)
    deserialized = event_schema.load(serialized)
    assert new_event_1 == deserialized
    new_event_2 = Second.factory(aggregate_id=aggregate_id, another_field="abc")
    assert new_event_2 == event_schema.loads(event_schema.dumps(new_event_2))


@pytest.mark.freeze_time("2020-08-09T20:00:00")
@pytest.mark.parametrize(
    "data",
    [
        {"some_field": "abc", "aggregate_version": 1, "created_at": "2020-08-09T20:00:00"},
        {"event_type": "First", "some_field": "abc", "aggregate_version": 1},
        {"event_type": "First", "another_field": "abc", "aggregate_version": 1, "created_at": "2020-08-09T20:00:00"},
        {
            "event_type": "First",
            "some_field": "abc",
            "extra_field": "abc",
            "aggregate_version": 1,
            "created_at": "2020-08-09T20:00:00",
        },
    ],
)
def test_deserialize_err(data, aggregate_id, event_schema):
    serialized = dict(data, aggregate_id=str(aggregate_id))
    with pytest.raises(ValidationError):
        event_schema.load(serialized)
