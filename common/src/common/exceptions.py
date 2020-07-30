class BaseEventException(Exception):
    """Base exception for events library"""


class InvalidSerializedEvent(BaseEventException):
    def __init__(self):
        super().__init__("Can't deserialize - event is invalid")


class UnregisteredEvent(BaseEventException):
    def __init__(self, clsname: str):
        super().__init__(f"{clsname} isn't a registered event in our system")


class EventVersionMismatch(BaseEventException):
    def __init__(self, clsname: str, current_version: int, event_version: int):
        super().__init__(
            f"Can't initialize {clsname} with version: {event_version}, current version: {current_version}"
        )
