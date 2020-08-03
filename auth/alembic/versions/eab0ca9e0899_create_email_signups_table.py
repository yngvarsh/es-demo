"""Create email_signups table

Revision ID: eab0ca9e0899
Revises: fee196f6ae3b
Create Date: 2020-08-03 11:11:16.667446

"""
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql

from alembic import op

revision = "eab0ca9e0899"
down_revision = "fee196f6ae3b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "email_signups",
        sa.Column("pk", sa.BigInteger(), nullable=False),
        sa.Column("user_id", postgresql.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=60), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("pk"),
        sa.UniqueConstraint("user_id", "email"),
    )
    op.create_index(op.f("ix_email_signups_email"), "email_signups", ["email"], unique=True)
    op.create_index(op.f("ix_email_signups_user_id"), "email_signups", ["user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_email_signups_user_id"), table_name="email_signups")
    op.drop_index(op.f("ix_email_signups_email"), table_name="email_signups")
    op.drop_table("email_signups")
