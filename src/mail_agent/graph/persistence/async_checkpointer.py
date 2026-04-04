"""
Checkpointer factory for LangGraph conversation persistence.

Provides two modes:
- MemorySaver: For development/testing (no persistence across restarts)
- AsyncPostgresSaver: For production (full persistence via PostgreSQL)

The AsyncPostgresSaver uses psycopg v3 async connection pool for efficient
concurrent access to checkpoint tables in a dedicated schema (default: ai_chat).
"""

import logging
from typing import TYPE_CHECKING

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from src.mail_agent.shared.settings import settings


if TYPE_CHECKING:
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg_pool import AsyncConnectionPool


logger = logging.getLogger(__name__)

# Module-level state for async checkpointer
_async_pool: "AsyncConnectionPool | None" = None
_async_checkpointer: "AsyncPostgresSaver | None" = None


async def create_async_checkpointer() -> "AsyncPostgresSaver":
    """
    Create AsyncPostgresSaver with a psycopg v3 async connection pool.

    Uses the database URL from settings with search_path set to the
    checkpointer schema. The pool is stored module-level for reuse.

    Returns:
        AsyncPostgresSaver instance ready for use with compiled graphs.

    Raises:
        RuntimeError: If called when pool already exists.
    """
    global _async_pool, _async_checkpointer

    if _async_pool is not None:
        raise RuntimeError("Async checkpointer pool already initialized")

    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg_pool import AsyncConnectionPool

    # Create async connection pool
    # min_size=1 ensures at least one connection is ready
    # max_size=10 allows concurrent checkpoint operations
    _async_pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        min_size=1,
        max_size=10,
        open=False,  # We'll open explicitly
    )
    await _async_pool.open()

    # Create checkpointer from pool
    _async_checkpointer = AsyncPostgresSaver(_async_pool)

    logger.info("Async checkpointer initialized successfully")
    return _async_checkpointer


async def close_async_checkpointer() -> None:
    """
    Close the async connection pool on application shutdown.

    Safe to call even if pool was never created.
    """
    global _async_pool, _async_checkpointer

    if _async_pool is not None:
        logger.info("Closing async checkpointer connection pool")
        await _async_pool.close()
        _async_pool = None
        _async_checkpointer = None


def get_checkpointer() -> BaseCheckpointSaver:
    """
    Get the active checkpointer instance.

    Returns:
        AsyncPostgresSaver if initialized (production), else MemorySaver (dev).
    """
    if _async_checkpointer is not None:
        return _async_checkpointer
    return MemorySaver()