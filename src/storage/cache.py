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
Caching utilities for DevAssist.

This module provides embedding and query result caching to reduce
redundant API calls and improve performance. Features:
- LRU-like eviction using OrderedDict
- Cache statistics tracking
- Periodic persistence to disk
"""

import gc
import json
import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from src.core.config import get_config
from src.core.context import get_context
from src.core.constants import (
    QUERY_CACHE_MAX_SIZE,
    QUERY_CACHE_TARGET_SIZE,
    QUERY_CACHE_SAVE_INTERVAL,
    EMBEDDING_CACHE_MAX_SIZE,
    EMBEDDING_CACHE_TARGET_SIZE,
    EMBEDDING_CACHE_SAVE_INTERVAL,
)

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Statistics for cache performance monitoring."""

    embedding_hits: int = 0
    embedding_misses: int = 0
    query_hits: int = 0
    query_misses: int = 0
    embedding_saves: int = 0
    query_saves: int = 0

    def embedding_hit_rate(self) -> float:
        """Calculate embedding cache hit rate."""
        total = self.embedding_hits + self.embedding_misses
        return self.embedding_hits / total if total > 0 else 0.0

    def query_hit_rate(self) -> float:
        """Calculate query cache hit rate."""
        total = self.query_hits + self.query_misses
        return self.query_hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, int | float]:
        """Export stats as dictionary."""
        return {
            "embedding_hits": self.embedding_hits,
            "embedding_misses": self.embedding_misses,
            "embedding_hit_rate": round(self.embedding_hit_rate() * 100, 1),
            "query_hits": self.query_hits,
            "query_misses": self.query_misses,
            "query_hit_rate": round(self.query_hit_rate() * 100, 1),
        }


# Global cache statistics
_cache_stats: Optional[CacheStats] = None


def get_cache_stats() -> CacheStats:
    """Get or create the global cache statistics instance."""
    global _cache_stats
    if _cache_stats is None:
        _cache_stats = CacheStats()
    return _cache_stats


def reset_cache_stats() -> None:
    """Reset cache statistics (useful for testing)."""
    global _cache_stats
    _cache_stats = CacheStats()


def load_embedding_cache() -> Dict[str, List[float]]:
    """
    Load embedding cache from disk.

    Returns:
        Dictionary mapping text to embedding vectors

    Side Effects:
        Updates the embedding_cache in ApplicationContext
    """
    config = get_config()
    ctx = get_context()

    try:
        if os.path.exists(config.embedding_cache_file):
            with open(config.embedding_cache_file, "r") as f:
                cache_data = json.load(f)
            ctx.embedding_cache.update(cache_data)
            if config.verbose_logging:
                logger.debug(f"Loaded {len(cache_data)} cached embeddings")
            return cache_data
    except Exception as e:
        logger.warning(f"Failed to load embedding cache: {e}")

    return {}


def save_embedding_cache() -> None:
    """
    Save embedding cache to disk.

    Applies LRU-like eviction if cache exceeds max size.
    """
    config = get_config()
    ctx = get_context()
    stats = get_cache_stats()

    try:
        embedding_cache = ctx.embedding_cache

        # Apply LRU eviction if cache is too large
        if len(embedding_cache) > EMBEDDING_CACHE_MAX_SIZE:
            # Convert to OrderedDict to preserve insertion order
            items = list(embedding_cache.items())
            # Keep the most recent entries (last N items)
            embedding_cache.clear()
            embedding_cache.update(dict(items[-EMBEDDING_CACHE_TARGET_SIZE:]))
            if config.verbose_logging:
                logger.debug(
                    f"Evicted old embeddings: {EMBEDDING_CACHE_MAX_SIZE} -> "
                    f"{EMBEDDING_CACHE_TARGET_SIZE}"
                )

        with open(config.embedding_cache_file, "w") as f:
            json.dump(embedding_cache, f, separators=(",", ":"))

        # Security: restricting permissions to owner only
        try:
            os.chmod(config.embedding_cache_file, 0o600)
        except Exception:
            # Non-critical if chmod fails (e.g. windows or odd filesystem)
            pass

        stats.embedding_saves += 1

        if config.verbose_logging:
            logger.debug(f"Saved {len(embedding_cache)} embedding cache entries")

    except Exception as e:
        logger.warning(f"Failed to save embedding cache: {e}")


def get_cached_embedding(text: str) -> Optional[List[float]]:
    """
    Get embedding from cache if available.

    Args:
        text: Text to look up

    Returns:
        Cached embedding vector or None if not found
    """
    ctx = get_context()
    stats = get_cache_stats()

    if text in ctx.embedding_cache:
        stats.embedding_hits += 1
        return ctx.embedding_cache[text]

    stats.embedding_misses += 1
    return None


def cache_embedding(text: str, embedding: List[float]) -> None:
    """
    Store embedding in cache and auto-save if interval reached.

    Args:
        text: Text that was embedded
        embedding: Resulting embedding vector
    """
    ctx = get_context()
    ctx.embedding_cache[text] = embedding

    # Auto-save at intervals
    if len(ctx.embedding_cache) % EMBEDDING_CACHE_SAVE_INTERVAL == 0:
        save_embedding_cache()


def load_query_cache() -> Dict[str, List[str]]:
    """
    Load query result cache from disk.

    Returns:
        Dictionary mapping query keys to cached results

    Side Effects:
        Updates the query_cache in ApplicationContext
    """
    config = get_config()
    ctx = get_context()

    try:
        if os.path.exists(config.query_cache_file):
            with open(config.query_cache_file, "r") as f:
                cache_data = json.load(f)
            ctx.query_cache.update(cache_data)
            if config.verbose_logging:
                logger.debug(f"Loaded {len(cache_data)} cached query results")
            return cache_data
    except Exception as e:
        logger.warning(f"Failed to load query cache: {e}")

    return {}


def save_query_cache() -> None:
    """
    Save query result cache to disk.

    Applies LRU-like eviction if cache exceeds max size.
    """
    config = get_config()
    ctx = get_context()
    stats = get_cache_stats()

    try:
        query_cache = ctx.query_cache

        # Apply LRU eviction if cache is too large
        if len(query_cache) > QUERY_CACHE_MAX_SIZE:
            items = list(query_cache.items())
            # Keep the most recent entries (last N items)
            query_cache.clear()
            query_cache.update(dict(items[-QUERY_CACHE_TARGET_SIZE:]))
            if config.verbose_logging:
                logger.debug(
                    f"Evicted old queries: {QUERY_CACHE_MAX_SIZE} -> "
                    f"{QUERY_CACHE_TARGET_SIZE}"
                )

        with open(config.query_cache_file, "w") as f:
            json.dump(query_cache, f, separators=(",", ":"))

        # Security: restricting permissions to owner only
        try:
            os.chmod(config.query_cache_file, 0o600)
        except Exception:
            pass

        stats.query_saves += 1

        if config.verbose_logging:
            logger.debug(f"Saved {len(query_cache)} query cache entries")

    except Exception as e:
        logger.warning(f"Failed to save query cache: {e}")


def get_cached_query(cache_key: str) -> Optional[List[str]]:
    """
    Get query result from cache if available.

    Args:
        cache_key: Cache key for the query

    Returns:
        Cached results or None if not found
    """
    ctx = get_context()
    stats = get_cache_stats()

    if cache_key in ctx.query_cache:
        stats.query_hits += 1
        return ctx.query_cache[cache_key]

    stats.query_misses += 1
    return None


def cache_query(cache_key: str, results: List[str]) -> None:
    """
    Store query result in cache and auto-save if interval reached.

    Args:
        cache_key: Cache key for the query
        results: Query results to cache
    """
    ctx = get_context()
    ctx.query_cache[cache_key] = results

    # Auto-save at intervals
    if len(ctx.query_cache) % QUERY_CACHE_SAVE_INTERVAL == 0:
        save_query_cache()


def cleanup_memory() -> None:
    """
    Force garbage collection to free memory.

    Should be called periodically during long-running operations
    to prevent memory buildup.
    """
    gc.collect()
    config = get_config()
    if config.verbose_logging:
        logger.debug("Memory cleanup completed")
