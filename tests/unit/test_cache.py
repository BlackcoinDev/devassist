#!/usr/bin/env python3
"""
Test suite for Cache Module (src/storage/cache.py).

Tests cover:
- Embedding cache loading and saving
- Query cache loading and saving
- Cache size limitation logic
- Cache clearing and memory cleanup
"""

import pytest
import os
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.storage.cache import (
    load_embedding_cache,
    load_query_cache,
    save_query_cache,
    cleanup_memory
)
from src.core.context import get_context, reset_context


class TestEmbeddingCache:
    """Test embedding cache operations."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_load_embedding_cache(self):
        """Test loading embeddings from disk."""
        data = {"test_text": [0.1, 0.2, 0.3]}
        with open(self.temp_file.name, 'w') as f:
            json.dump(data, f)

        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.embedding_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            loaded = load_embedding_cache()
            ctx = get_context()

            assert loaded == data
            assert ctx.embedding_cache == data

    def test_load_embedding_cache_file_not_found(self):
        """Test loading embeddings when file doesn't exist."""
        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.embedding_cache_file = "/nonexistent/file.json"
            mock_get_config.return_value = mock_config

            loaded = load_embedding_cache()
            ctx = get_context()

            assert loaded == {}
            assert ctx.embedding_cache == {}

    def test_load_embedding_cache_invalid_json(self):
        """Test loading embeddings with invalid JSON."""
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json")

        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.embedding_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            loaded = load_embedding_cache()
            ctx = get_context()

            assert loaded == {}
            assert ctx.embedding_cache == {}


class TestQueryCache:
    """Test query cache operations."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_load_query_cache(self):
        """Test loading query results from disk."""
        data = {"query_1": ["result1", "result2"]}
        with open(self.temp_file.name, 'w') as f:
            json.dump(data, f)

        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            loaded = load_query_cache()
            ctx = get_context()

            assert loaded == data
            assert ctx.query_cache == data

    def test_load_query_cache_file_not_found(self):
        """Test loading query cache when file doesn't exist."""
        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = "/nonexistent/file.json"
            mock_get_config.return_value = mock_config

            loaded = load_query_cache()
            ctx = get_context()

            assert loaded == {}
            assert ctx.query_cache == {}

    def test_load_query_cache_invalid_json(self):
        """Test loading query cache with invalid JSON."""
        with open(self.temp_file.name, 'w') as f:
            f.write("invalid json")

        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            loaded = load_query_cache()
            ctx = get_context()

            assert loaded == {}
            assert ctx.query_cache == {}


class TestCacheManagement:
    """Test cache cleanup and clearing."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_cleanup_memory(self):
        """Test memory cleanup triggers garbage collection."""
        with patch('gc.collect') as mock_collect:
            cleanup_memory()
            assert mock_collect.called

    def test_save_query_cache_limits_size(self):
        """Test that saving query cache enforces the 1000 entry limit."""
        ctx = get_context()
        # Create 1100 entries
        ctx.query_cache = {f"query_{i}": [f"result_{i}"] for i in range(1100)}

        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            save_query_cache()
            
            # Verify file contains only 500 entries (as per logic in cache.py)
            with open(self.temp_file.name, 'r') as f:
                saved_data = json.load(f)
            
            assert len(saved_data) == 500
            assert len(ctx.query_cache) == 500

    def test_save_query_cache_write_error(self):
        """Test saving query cache when write fails."""
        ctx = get_context()
        ctx.query_cache = {"query": ["result"]}

        with patch('src.storage.cache.get_config') as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = "/invalid/path/file.json"
            mock_get_config.return_value = mock_config

            # Should not raise exception, just log warning
            save_query_cache()
            
            # Cache should still be intact
            assert len(ctx.query_cache) == 1
