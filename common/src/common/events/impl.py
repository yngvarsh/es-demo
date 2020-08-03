from dataclasses import dataclass

from common.events import Event


@dataclass(frozen=True)
class UserSignedUp(Event):
    email: str
    password: str
