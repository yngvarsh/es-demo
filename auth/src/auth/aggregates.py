import os

from datetime import datetime, timedelta
from functools import singledispatchmethod
from typing import Awaitable, Optional, Tuple
from uuid import uuid4

import bcrypt
import jwt

from asyncpg import Record

from auth.tables import email_signups
from common.aggregate import AggregateRoot, attribute, command
from common.events import Event
from common.events.impl import UserSignedUp
from common.typing import ID


class User(AggregateRoot):
    email: str
    password: bytes
    token: bytes

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
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=30),
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

    async def get_email_signup(self, email: str) -> Optional[Record]:
        query = email_signups.select().where(email_signups.c.email == email)
        return await self.connection.fetchrow(query)

    async def add_email_signup(self, user_id: ID, email: str, password: str, created_at: datetime) -> None:
        query = email_signups.insert().values(user_id=user_id, email=email, password=password, created_at=created_at)
        await self.connection.execute(query)

    async def login(self, email: str, password: str) -> None:
        email_signup = await self.get_email_signup(email)
        assert email_signup, "User with specified email not exists"
        assert bcrypt.checkpw(password.encode("utf8"), email_signup["password"].encode("utf8")), "Invalid password"
        self.id = email_signup["user_id"]
        await self

    @command(lazy=False)
    async def sign_up(self, email: str, password: str) -> Optional[Tuple[UserSignedUp, Awaitable]]:
        email_signup_exists = await self.get_email_signup(email)
        assert not email_signup_exists, "User with specified email already exists"
        salt = bcrypt.gensalt(rounds=10)  # Salt length should be 29
        password = bcrypt.hashpw(password.encode("utf8"), salt).decode("utf8")  # Decode to string for storage
        event = UserSignedUp.factory(email=email, password=password)
        action = self.add_email_signup(event.aggregate_id, email, password, event.created_at)
        return event, action
