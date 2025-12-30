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
    save_embedding_cache,
    get_cached_embedding,
    cache_embedding,
    load_query_cache,
    save_query_cache,
    get_cached_query,
    cache_query,
    get_cache_stats,
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
    "save_embedding_cache",
    "get_cached_embedding",
    "cache_embedding",
    "load_query_cache",
    "save_query_cache",
    "get_cached_query",
    "cache_query",
    "get_cache_stats",
    "cleanup_memory",
]
