# MIT License
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
redundant API calls and improve performance.
"""

import gc
import json
import os
import logging
from typing import Dict, List

from src.core.config import get_config
from src.core.context import get_context

logger = logging.getLogger(__name__)


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
            logger.debug(f"Loaded {len(cache_data)} cached embeddings")
            return cache_data
    except Exception as e:
        logger.warning(f"Failed to load embedding cache: {e}")

    return {}


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
            logger.debug(f"Loaded {len(cache_data)} cached query results")
            return cache_data
    except Exception as e:
        logger.warning(f"Failed to load query cache: {e}")

    return {}


def save_query_cache() -> None:
    """
    Save query result cache to disk.

    Limits cache size to 500 most recent entries if it exceeds 1000.
    """
    config = get_config()
    ctx = get_context()

    try:
        query_cache = ctx.query_cache

        # Limit cache size
        if len(query_cache) > 1000:
            items = list(query_cache.items())
            # Keep the 500 most recent items
            query_cache.clear()
            query_cache.update(dict(items[-500:]))

        with open(config.query_cache_file, "w") as f:
            json.dump(query_cache, f, separators=(",", ":"))

        logger.debug(f"Saved {len(query_cache)} query cache entries")

    except Exception as e:
        logger.warning(f"Failed to save query cache: {e}")


def cleanup_memory() -> None:
    """
    Force garbage collection to free memory.

    Should be called periodically during long-running operations
    to prevent memory buildup.
    """
    gc.collect()
    logger.debug("Memory cleanup completed")
