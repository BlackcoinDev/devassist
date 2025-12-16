"""
Database management for DevAssist.

This module handles SQLite database initialization and connection management
for conversation history persistence.
"""

import sqlite3
import threading
import logging
from typing import Optional, Tuple

from src.core.config import get_config
from src.core.context import get_context, set_db_conn, set_db_lock

logger = logging.getLogger(__name__)


def initialize_database() -> Tuple[Optional[sqlite3.Connection], Optional[threading.Lock]]:
    """
    Initialize the SQLite database connection.

    Creates the database file and conversations table if they don't exist.
    Sets up thread-safe connection with proper locking.

    Returns:
        Tuple of (connection, lock) or (None, None) if initialization fails

    Side Effects:
        - Creates database file at configured DB_PATH
        - Creates conversations table if not exists
        - Updates ApplicationContext with db_conn and db_lock
    """
    config = get_config()

    if config.db_type != "sqlite":
        logger.warning(f"Unsupported database type: {config.db_type}")
        return None, None

    try:
        # Create connection with check_same_thread=False for multi-threaded access
        db_conn = sqlite3.connect(config.db_path, check_same_thread=False)
        db_lock = threading.Lock()

        # Create conversations table if it doesn't exist
        with db_lock:
            cursor = db_conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db_conn.commit()

        # Update context with database connection
        set_db_conn(db_conn)
        set_db_lock(db_lock)

        logger.debug(f"SQLite database initialized at {config.db_path}")
        return db_conn, db_lock

    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")
        return None, None


def get_database_connection() -> Tuple[Optional[sqlite3.Connection], Optional[threading.Lock]]:
    """
    Get the current database connection from context.

    Returns:
        Tuple of (connection, lock) from ApplicationContext
    """
    ctx = get_context()
    return ctx.db_conn, ctx.db_lock


def close_database() -> None:
    """
    Close the database connection.

    Should be called during application shutdown.
    """
    ctx = get_context()
    if ctx.db_conn is not None:
        try:
            ctx.db_conn.close()
            logger.debug("Database connection closed")
        except Exception as e:
            logger.warning(f"Error closing database: {e}")
        finally:
            set_db_conn(None)
            set_db_lock(None)
