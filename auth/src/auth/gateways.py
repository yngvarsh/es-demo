from datetime import datetime
from typing import Optional

from auth.tables import email_signups
from common.aggregate import Gateway
from common.typing import ID


class UserGateway(Gateway):
    async def get_email_signup(self, email: str) -> Optional[ID]:
        query = (
            email_signups.select().where(email_signups.c.email == email).with_only_columns([email_signups.c.user_id])
        )
        return await self.connection.fetchval(query)

    async def add_email_signup(self, user_id: ID, email: str, password: str, created_at: datetime) -> None:
        query = email_signups.insert().values(user_id=user_id, email=email, password=password, created_at=created_at)
        await self.connection.execute(query)
