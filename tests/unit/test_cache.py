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
Test suite for Cache Module (src/storage/cache.py).

Tests cover:
- Embedding cache loading and saving
- Query cache loading and saving
- Cache size limitation logic
- Cache clearing and memory cleanup
"""

import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.storage.cache import (
    load_embedding_cache,
    load_query_cache,
    save_query_cache,
    cleanup_memory,
)
from src.core.context import get_context, reset_context


class TestEmbeddingCache:
    """Test embedding cache operations."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_load_embedding_cache(self):
        """Test loading embeddings from disk."""
        data = {"test_text": [0.1, 0.2, 0.3]}
        with open(self.temp_file.name, "w") as f:
            json.dump(data, f)

        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.embedding_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            loaded = load_embedding_cache()
            ctx = get_context()

            assert loaded == data
            assert ctx.embedding_cache == data

    def test_load_embedding_cache_file_not_found(self):
        """Test loading embeddings when file doesn't exist."""
        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.embedding_cache_file = "/nonexistent/file.json"
            mock_get_config.return_value = mock_config

            loaded = load_embedding_cache()
            ctx = get_context()

            assert loaded == {}
            assert ctx.embedding_cache == {}

    def test_load_embedding_cache_invalid_json(self):
        """Test loading embeddings with invalid JSON."""
        with open(self.temp_file.name, "w") as f:
            f.write("invalid json")

        with patch("src.storage.cache.get_config") as mock_get_config:
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
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_load_query_cache(self):
        """Test loading query results from disk."""
        data = {"query_1": ["result1", "result2"]}
        with open(self.temp_file.name, "w") as f:
            json.dump(data, f)

        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            loaded = load_query_cache()
            ctx = get_context()

            assert loaded == data
            assert ctx.query_cache == data

    def test_load_query_cache_file_not_found(self):
        """Test loading query cache when file doesn't exist."""
        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = "/nonexistent/file.json"
            mock_get_config.return_value = mock_config

            loaded = load_query_cache()
            ctx = get_context()

            assert loaded == {}
            assert ctx.query_cache == {}

    def test_load_query_cache_invalid_json(self):
        """Test loading query cache with invalid JSON."""
        with open(self.temp_file.name, "w") as f:
            f.write("invalid json")

        with patch("src.storage.cache.get_config") as mock_get_config:
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
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_cleanup_memory(self):
        """Test memory cleanup triggers garbage collection."""
        with patch("gc.collect") as mock_collect:
            cleanup_memory()
            assert mock_collect.called

    def test_save_query_cache_limits_size(self):
        """Test that saving query cache enforces the 1000 entry limit."""
        ctx = get_context()
        # Create 1100 entries
        ctx.query_cache = {f"query_{i}": [f"result_{i}"] for i in range(1100)}

        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            save_query_cache()

            # Verify file contains only 500 entries (as per logic in cache.py)
            with open(self.temp_file.name, "r") as f:
                saved_data = json.load(f)

            assert len(saved_data) == 500
            assert len(ctx.query_cache) == 500

    def test_save_query_cache_write_error(self):
        """Test saving query cache when write fails."""
        ctx = get_context()
        ctx.query_cache = {"query": ["result"]}

        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.query_cache_file = "/invalid/path/file.json"
            mock_get_config.return_value = mock_config

            # Should not raise exception, just log warning
            save_query_cache()

            # Cache should still be intact
            assert len(ctx.query_cache) == 1


class TestNewCacheFeatures:
    """Test new cache features (auto-save, stats, embedding save)."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.temp_file.close()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
        reset_context()

    def test_save_embedding_cache_limits_size(self):
        """Test that saving embedding cache enforces max size limits."""
        ctx = get_context()
        from src.storage.cache import (
            save_embedding_cache,
            EMBEDDING_CACHE_MAX_SIZE,
            EMBEDDING_CACHE_TARGET_SIZE,
        )

        # Populate cache with more items than limit
        ctx.embedding_cache = {f"text_{i}": [0.1] for i in range(EMBEDDING_CACHE_MAX_SIZE + 100)}

        with patch("src.storage.cache.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.embedding_cache_file = self.temp_file.name
            mock_config.verbose_logging = True
            mock_get_config.return_value = mock_config

            save_embedding_cache()

            # Verify file contains target size
            with open(self.temp_file.name, "r") as f:
                saved_data = json.load(f)

            assert len(saved_data) == EMBEDDING_CACHE_TARGET_SIZE
            assert len(ctx.embedding_cache) == EMBEDDING_CACHE_TARGET_SIZE

    def test_auto_save_trigger(self):
        """Test that cache_embedding triggers auto-save."""
        from src.storage.cache import cache_embedding, EMBEDDING_CACHE_SAVE_INTERVAL

        ctx = get_context()
        # Fill just before trigger (interval - 1)
        # Note: We need to mock save_embedding_cache inside the module

        # Since we can't easily patch imported function inside module
        # cache.py defines save_embedding_cache, so we can patch it
        # Populate context up to trigger point
        ctx.embedding_cache = {f"k{i}": [0.1] for i in range(EMBEDDING_CACHE_SAVE_INTERVAL - 1)}

        with patch("src.storage.cache.save_embedding_cache") as mock_save:
            # Add one more to reach interval
            cache_embedding("trigger", [0.1])
            assert mock_save.called

    def test_cache_stats(self):
        """Test cache statistics tracking."""
        from src.storage.cache import get_cache_stats, reset_cache_stats, get_cached_embedding

        reset_cache_stats()
        stats = get_cache_stats()

        ctx = get_context()
        ctx.embedding_cache["exist"] = [0.1]

        # Hit
        val = get_cached_embedding("exist")
        assert val is not None
        assert stats.embedding_hits == 1

        # Miss
        val = get_cached_embedding("missing")
        assert val is None
        assert stats.embedding_misses == 1

        # Hit rate
        assert stats.embedding_hit_rate() == 0.5

    def test_cache_permissions(self):
        """Test that cache files are secured with 0o600 permissions."""
        from src.storage.cache import save_embedding_cache, save_query_cache

        ctx = get_context()
        ctx.embedding_cache = {"k": [0.1]}
        ctx.query_cache = {"q": ["r"]}

        # We need to mock os.chmod to verify it's called
        with patch("os.chmod") as mock_chmod, \
                patch("src.storage.cache.get_config") as mock_get_config:

            mock_config = MagicMock()
            mock_config.embedding_cache_file = self.temp_file.name
            mock_config.query_cache_file = self.temp_file.name
            mock_get_config.return_value = mock_config

            save_embedding_cache()
            mock_chmod.assert_called_with(self.temp_file.name, 0o600)

            mock_chmod.reset_mock()

            save_query_cache()
            mock_chmod.assert_called_with(self.temp_file.name, 0o600)
