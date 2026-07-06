# env.py
# Purpose: Alembic migrations environment execution script.
# Responsibilities:
#   - Load declarative model metadata for database autogenerate schemas mapping
#   - Execute migrations in offline or async online mode
# DO NOT: Hardcode database credentials (read from settings.DATABASE_URL).
# DO NOT: Bypass async event loop handling under online migration runs.

import asyncio
import logging
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

from app.core.config import settings
from app.db.base import Base
# Import all database models to register metadata for Alembic autogenerate
from app.models import user, startup, chat, report  # noqa: F401

logger = logging.getLogger(__name__)

# Interpret the config file for Python logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set model metadata target for schema comparisons
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    logger.info("Executing migrations in offline mode.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Helper running migrations inside a sync connection wrapper."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Establish async engine and run online schema alterations."""
    url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    logger.info(f"Connecting to database for online migrations...")

    connectable = create_async_engine(
        url,
        poolclass=pool.NullPool,
    )

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (async execution loop)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
