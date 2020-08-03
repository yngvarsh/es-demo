from datetime import datetime
from uuid import uuid4

import pytest

from aioredis import Redis
from asyncpg.connection import Connection
from asyncpgsa.transactionmanager import ConnectionTransactionContextManager
from asynctest import CoroutineMock, MagicMock

from .fake import EventSchema, First, Second


@pytest.fixture
def now():
    return datetime(2020, 8, 9, 20)


@pytest.fixture
def aggregate_id():
    return uuid4()


@pytest.fixture
def events(aggregate_id, now):
    return [
        First.factory(aggregate_id=aggregate_id, aggregate_version=0, created_at=now, some_field="foo"),
        Second.factory(aggregate_id=aggregate_id, aggregate_version=1, created_at=now, another_field="one"),
        First.factory(aggregate_id=aggregate_id, aggregate_version=2, created_at=now, some_field="bar"),
        Second.factory(aggregate_id=aggregate_id, aggregate_version=3, created_at=now, another_field="two"),
        First.factory(aggregate_id=aggregate_id, aggregate_version=4, created_at=now, some_field="baz"),
    ]


@pytest.fixture
def stored_events(aggregate_id, now):
    return [
        dict(
            pk=1,
            aggregate_id=aggregate_id,
            aggregate_version=0,
            state='{"some_field": "foo", "aggregate_id": "%s", "aggregate_version": 0, "created_at": "%s", "event_type": "First"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            initial='{"some_field": "foo", "aggregate_id": "%s", "aggregate_version": 0, "created_at": "%s", "event_type": "First"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            created_at=now,
        ),
        dict(
            pk=2,
            aggregate_id=aggregate_id,
            aggregate_version=1,
            state='{"another_field": "one", "aggregate_id": "%s", "aggregate_version": 1, "created_at": "%s", "event_type": "Second"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            initial='{"another_field": "one", "aggregate_id": "%s", "aggregate_version": 1, "created_at": "%s", "event_type": "Second"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            created_at=now,
        ),
        dict(
            pk=3,
            aggregate_id=aggregate_id,
            aggregate_version=2,
            state='{"some_field": "bar", "aggregate_id": "%s", "aggregate_version": 2, "created_at": "%s", "event_type": "First"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            initial='{"some_field": "bar", "aggregate_id": "%s", "aggregate_version": 2, "created_at": "%s", "event_type": "First"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            created_at=now,
        ),
        dict(
            pk=4,
            aggregate_id=aggregate_id,
            aggregate_version=3,
            state='{"another_field": "two", "aggregate_id": "%s", "aggregate_version": 3, "created_at": "%s", "event_type": "Second"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            initial='{"another_field": "two", "aggregate_id": "%s", "aggregate_version": 3, "created_at": "%s", "event_type": "Second"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            created_at=now,
        ),
        dict(
            pk=5,
            aggregate_id=aggregate_id,
            aggregate_version=4,
            state='{"some_field": "baz", "aggregate_id": "%s", "aggregate_version": 4, "created_at": "%s", "event_type": "First"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            initial='{"some_field": "baz", "aggregate_id": "%s", "aggregate_version": 4, "created_at": "%s", "event_type": "First"}'  # noqa: E501
            % (str(aggregate_id), now.isoformat()),
            created_at=now,
        ),
    ]


@pytest.fixture
def event_schema():
    return EventSchema()


@pytest.fixture
def connection(stored_events, aggregate_id):
    c = MagicMock(Connection)
    cursor = MagicMock()
    cursor.__aiter__.return_value = stored_events
    c.cursor.return_value = cursor
    return c


@pytest.fixture
def transaction(connection):
    t = MagicMock(ConnectionTransactionContextManager)
    t.__aenter__.return_value = connection
    return t


@pytest.fixture
def redis():
    r = MagicMock(Redis)
    r.publish = CoroutineMock()
    return r
