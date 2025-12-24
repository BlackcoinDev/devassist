import sqlite3
import logging
from typing import Dict, List, Optional

from src.core.config import get_config

logger = logging.getLogger(__name__)


def initialize_mem0_local() -> Dict[str, str]:
    """Initialize local Mem0-like memory tables in SQLite."""

    config = get_config()
    db_path = config.db_path

    try:
        logger.debug(f"Initializing Mem0 local at {db_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mem0_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Created mem0_preferences table")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mem0_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default_user',
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.debug("Created mem0_memories table")

        conn.commit()
        conn.close()

        status = {
            "mem0_preferences": "✅ Created",
            "mem0_memories": "✅ Created",
            "database": db_path,
        }

        logger.info(f"Mem0 local initialized: {status}")
        return status

    except Exception as e:
        logger.error(f"Failed to initialize Mem0 local: {e}")
        return {
            "mem0_preferences": "❌ Failed",
            "mem0_memories": "❌ Failed",
            "database": db_path,
        }


def add_preference(key: str, value: str, user_id: str = "default_user") -> bool:
    """Add or update a user preference in Mem0 local memory."""

    config = get_config()
    db_path = config.db_path

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO mem0_preferences (key, value, user_id)
            VALUES (?, ?, ?)
        """, (key, value, user_id))

        conn.commit()
        conn.close()

        logger.debug(f"Set preference {key}={value} for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to add preference: {e}")
        return False


def get_preference(key: str, user_id: str = "default_user") -> Optional[str]:
    """Get a user preference from Mem0 local memory."""

    config = get_config()
    db_path = config.db_path

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT value FROM mem0_preferences
            WHERE key = ? AND user_id = ?
        """, (key, user_id))
        result = cursor.fetchone()

        conn.close()

        if result:
            value = result[0]
            logger.debug(f"Got preference {key}={value} for user {user_id}")
            return value
        else:
            logger.debug(f"Preference {key} not found for user {user_id}")
            return None

    except Exception as e:
        logger.error(f"Failed to get preference: {e}")
        return None


def add_memory(content: str, user_id: str = "default_user") -> bool:
    """Add a memory (fact/preference) to Mem0 local memory."""

    config = get_config()
    db_path = config.db_path

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO mem0_memories (user_id, content, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (user_id, content))

        conn.commit()
        conn.close()

        logger.debug(f"Added memory for user {user_id}: {content[:50]}...")
        return True

    except Exception as e:
        logger.error(f"Failed to add memory: {e}")
        return False


def get_memories(user_id: str = "default_user") -> List[Dict]:
    """Get all memories for a user from Mem0 local memory."""

    config = get_config()
    db_path = config.db_path

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content, created_at FROM mem0_memories
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 100
        """, (user_id,))

        rows = cursor.fetchall()

        conn.close()

        memories = [
            {"id": row[0], "content": row[1], "created_at": row[2]}
            for row in rows
        ]

        logger.debug(f"Retrieved {len(memories)} memories for user {user_id}")
        return memories

    except Exception as e:
        logger.error(f"Failed to get memories: {e}")
        return []


def search_memories(query: str, user_id: str = "default_user") -> List[Dict]:
    """Search memories by content in Mem0 local memory."""

    config = get_config()
    db_path = config.db_path

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        search_pattern = f"%{query}%"

        cursor.execute("""
            SELECT id, content, created_at FROM mem0_memories
            WHERE user_id = ? AND content LIKE ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (user_id, search_pattern))

        rows = cursor.fetchall()

        conn.close()

        memories = [
            {"id": row[0], "content": row[1], "created_at": row[2]}
            for row in rows
        ]

        logger.debug(f"Found {len(memories)} memories matching '{query}' for user {user_id}")
        return memories

    except Exception as e:
        logger.error(f"Failed to search memories: {e}")
        return []


__all__ = [
    "initialize_mem0_local",
    "add_preference",
    "get_preference",
    "add_memory",
    "get_memories",
    "search_memories",
]
