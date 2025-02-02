import os

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from auth.tables import metadata

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    "postgresql+psycopg2://%s:%s@%s:%s/%s"
    % (
        os.getenv("POSTGRES_USER", "auth"),
        os.getenv("POSTGRES_PASSWORD", "auth"),
        os.getenv("POSTGRES_HOST", "localhost"),
        os.getenv("POSTGRES_PORT", 5432),
        os.getenv("POSTGRES_DB", "auth"),
    ),
)

fileConfig(config.config_file_name)

target_metadata = metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
