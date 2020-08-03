from sqlalchemy import BigInteger, Column, DateTime, String, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from common.dal import metadata, stored_events  # noqa: F401

email_signups = Table(
    "email_signups",
    metadata,
    Column("pk", BigInteger, primary_key=True),
    Column("user_id", UUID, nullable=False, index=True),
    Column("email", String(255), nullable=False, index=True, unique=True),
    Column("password", String(60), nullable=False),
    Column("created_at", DateTime, nullable=False),
    UniqueConstraint("user_id", "email"),
)
