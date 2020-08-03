import os

from datetime import datetime, timedelta
from functools import singledispatchmethod
from typing import Awaitable, Optional, Tuple
from uuid import uuid4

import bcrypt
import jwt

from auth.gateways import UserGateway
from common.aggregate import AggregateRoot, attribute, command
from common.events import Event
from common.events.impl import UserSignedUp


class User(AggregateRoot):
    email: str
    password: bytes
    token: bytes
    gateway: UserGateway

    @attribute
    def email(self) -> str:
        return self.state["email"]

    @attribute
    def password(self) -> bytes:
        return self.state["password"]

    @attribute
    def token(self) -> str:
        assert self.id, "User wasn't created"
        return jwt.encode(
            {
                "sub": str(self.id),
                "jti": str(uuid4()),
                "iat": int(datetime.utcnow().timestamp()),
                "exp": int((datetime.utcnow() + timedelta(days=1)).timestamp()),
            },
            key=os.environ["AUTH_SECRET"],
        ).decode("utf8")

    @singledispatchmethod
    def apply_event(self, event: Event) -> None:
        raise NotImplementedError

    @apply_event.register
    def _(self, event: UserSignedUp) -> None:
        self.id = event.aggregate_id
        self.state["email"] = event.email
        self.state["password"] = event.password

    @command(lazy=False)
    async def sign_up(self, email: str, password: str) -> Optional[Tuple[UserSignedUp, Awaitable]]:
        email_signup_exists = await self.gateway.get_email_signup(email)
        assert not email_signup_exists, "User with specified email already exists"
        salt = bcrypt.gensalt(rounds=10)  # Salt length should be 29
        password = bcrypt.hashpw(password.encode("utf8"), salt).decode("utf8")  # Decode to string for storage
        event = UserSignedUp.factory(email=email, password=password)
        action = self.gateway.add_email_signup(event.aggregate_id, email, password, event.created_at)
        return event, action
