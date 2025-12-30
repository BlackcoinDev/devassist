#
# Copyright (c) 2025 BlackcoinDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Database management for DevAssist.

This module handles SQLite database initialization, connection management,
and schema versioning for conversation history persistence.
"""

import sqlite3
import threading
import logging
from typing import Optional, Tuple

from src.core.config import get_config
from src.core.context import get_context, set_db_conn, set_db_lock

logger = logging.getLogger(__name__)

# Current schema version - increment when making schema changes
SCHEMA_VERSION = 1


def _get_schema_version(cursor: sqlite3.Cursor) -> int:
    """
    Get the current schema version from the database.

    Returns:
        Current schema version, or 0 if not set
    """
    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='schema_version'"
        )
        if not cursor.fetchone():
            return 0

        cursor.execute(
            "SELECT version FROM schema_version ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


def _set_schema_version(cursor: sqlite3.Cursor, version: int) -> None:
    """Set the schema version in the database."""
    cursor.execute(
        "INSERT INTO schema_version (version) VALUES (?)",
        (version,)
    )


def _run_migrations(cursor: sqlite3.Cursor, current_version: int) -> int:
    """
    Run database migrations from current_version to SCHEMA_VERSION.

    Args:
        cursor: Database cursor
        current_version: Current schema version in database

    Returns:
        Final schema version after migrations
    """
    if current_version >= SCHEMA_VERSION:
        return current_version

    logger.info(f"Migrating database from v{current_version} to v{SCHEMA_VERSION}")

    # Migration from v0 to v1: Initial schema
    if current_version < 1:
        # Create schema_version table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create conversations table (if not exists for fresh installs)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create index for faster queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_conversations_session
            ON conversations(session_id, timestamp)
            """
        )

        _set_schema_version(cursor, 1)
        logger.info("Applied migration: v0 -> v1 (initial schema)")

    # Future migrations go here:
    # if current_version < 2:
    #     cursor.execute("ALTER TABLE conversations ADD COLUMN tool_call_id TEXT")
    #     _set_schema_version(cursor, 2)
    #     logger.info("Applied migration: v1 -> v2 (added tool_call_id)")

    return SCHEMA_VERSION


def initialize_database() -> (
    Tuple[Optional[sqlite3.Connection], Optional[threading.Lock]]
):
    """
    Initialize the SQLite database connection.

    Creates the database file and tables if they don't exist.
    Runs any pending schema migrations.
    Sets up thread-safe connection with proper locking.

    Returns:
        Tuple of (connection, lock) or (None, None) if initialization fails

    Side Effects:
        - Creates database file at configured DB_PATH
        - Creates/migrates database schema
        - Updates ApplicationContext with db_conn and db_lock
    """
    config = get_config()

    if config.db_type != "sqlite":
        logger.warning(f"Unsupported database type: {config.db_type}")
        return None, None

    try:
        # Create connection with check_same_thread=False for multi-threaded access
        # timeout=30.0 prevents hanging on locked database
        db_conn = sqlite3.connect(
            config.db_path, check_same_thread=False, timeout=30.0
        )
        db_lock = threading.Lock()

        # Configure database and run migrations
        with db_lock:
            cursor = db_conn.cursor()

            # Enable WAL mode for better concurrent read/write performance
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")

            # Check current version and run migrations
            current_version = _get_schema_version(cursor)
            _run_migrations(cursor, current_version)

            db_conn.commit()

        # Update context with database connection
        set_db_conn(db_conn)
        set_db_lock(db_lock)

        logger.debug(
            f"SQLite database initialized at {config.db_path} (schema v{SCHEMA_VERSION})"
        )
        return db_conn, db_lock

    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")
        return None, None


def get_database_connection() -> (
    Tuple[Optional[sqlite3.Connection], Optional[threading.Lock]]
):
    """
    Get the current database connection from context.

    Returns:
        Tuple of (connection, lock) from ApplicationContext
    """
    ctx = get_context()
    return ctx.db_conn, ctx.db_lock
