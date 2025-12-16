"""
Storage module for DevAssist.

This module provides data persistence functionality including:
- SQLite database management for conversation history
- Embedding and query caching
- Memory management utilities

All storage operations are thread-safe and use the ApplicationContext
for accessing database connections.
"""

from src.storage.database import (
    initialize_database,
    get_database_connection,
)
from src.storage.memory import (
    load_memory,
    save_memory,
    trim_history,
)
from src.storage.cache import (
    load_embedding_cache,
    load_query_cache,
    save_query_cache,
    cleanup_memory,
)

__all__ = [
    # Database
    "initialize_database",
    "get_database_connection",
    # Memory
    "load_memory",
    "save_memory",
    "trim_history",
    # Cache
    "load_embedding_cache",
    "load_query_cache",
    "save_query_cache",
    "cleanup_memory",
]
