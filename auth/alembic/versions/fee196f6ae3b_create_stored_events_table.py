"""Create stored_events table

Revision ID: fee196f6ae3b
Revises:
Create Date: 2020-08-03 11:09:11.350689

"""
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

from alembic import op

revision = "fee196f6ae3b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "stored_events",
        sa.Column("pk", sa.BigInteger(), nullable=False),
        sa.Column("aggregate_id", postgresql.UUID(), nullable=False),
        sa.Column("aggregate_version", sa.Integer(), nullable=False),
        sa.Column("state", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("initial", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("aggregate_id", "aggregate_version"),
    )


def downgrade():
    op.drop_table("stored_events")
