"""Checkpointer adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver


def build_checkpointer(
    kind: str = "memory", database_url: str | None = None
) -> BaseCheckpointSaver | None:
    """Return a LangGraph checkpointer.

    TODO(student): add SQLite/Postgres support for the extension track.
    The starter uses MemorySaver so the lab can run without infrastructure.
    """
    if kind == "none":
        return None
    if kind == "memory":
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()
    if kind == "sqlite":
        import sqlite3
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver  # type: ignore[import-not-found]
        except ImportError as exc:
            msg = "SQLite checkpointer requires: pip install langgraph-checkpoint-sqlite"
            raise RuntimeError(msg) from exc
        
        conn = sqlite3.connect(database_url or "checkpoints.db", check_same_thread=False)
        # Enable WAL mode for production hygiene
        conn.execute("PRAGMA journal_mode=WAL")
        return SqliteSaver(conn)
    if kind == "postgres":
        try:
            from langgraph.checkpoint.postgres import (  # type: ignore[import-not-found]
                PostgresSaver,
            )
        except ImportError as exc:
            msg = "Postgres checkpointer requires: pip install langgraph-checkpoint-postgres"
            raise RuntimeError(msg) from exc
        return PostgresSaver.from_conn_string(database_url or "")
    raise ValueError(f"Unknown checkpointer kind: {kind}")
