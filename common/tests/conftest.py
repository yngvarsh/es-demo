from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

import pytest

from common.events import Event


@pytest.fixture
def now():
    return datetime(2020, 8, 9, 20)


@pytest.fixture
def aggregate_id():
    return uuid4()


@pytest.fixture
def event_subclass():
    @dataclass(frozen=True)
    class Dummy(Event):
        some_field: str
        current_version = 2

    return Dummy
