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
Test suite for Spaces Module (src/vectordb/spaces.py).

Tests cover:
- Space name mapping to collection names
- Listing spaces by parsing collection names
- Space deletion restrictions
- Space switching and persistence
"""

import os
import json
from unittest.mock import patch, MagicMock
from src.vectordb.spaces import (
    get_space_collection_name,
    list_spaces,
    delete_space,
    switch_space,
    save_current_space,
    load_current_space,
)
from src.core.context import get_context, reset_context


class TestSpaceManagement:
    """Test space creation, listing, and deletion."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists("space_settings.json"):
            os.remove("space_settings.json")
        reset_context()

    def test_get_space_collection_name(self):
        """Test name mapping logic."""
        assert get_space_collection_name("default") == "knowledge_base"
        assert get_space_collection_name("my_project") == "space_my_project"

    def test_list_spaces(self):
        """Test listing spaces from collections."""
        mock_collections = [
            {"name": "knowledge_base"},
            {"name": "some_other_coll"},
            {"name": "space_project_a"},
            {"name": "space_project_b"},
        ]

        with patch("src.vectordb.spaces.get_chromadb_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.list_collections.return_value = mock_collections

            spaces = list_spaces()

            assert "default" in spaces
            assert "project_a" in spaces
            assert "project_b" in spaces
            assert len(spaces) == 3

    def test_delete_space_restrictions(self):
        """Test that default space cannot be deleted."""
        assert delete_space("default") is False

    def test_delete_space_calls_client(self):
        """Test that delete_space calls the underlying client."""
        with patch("src.vectordb.spaces.get_chromadb_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.delete_collection.return_value = True

            success = delete_space("project_x")

            assert success is True
            mock_client.delete_collection.assert_called_with("space_project_x")


class TestSpaceSwitching:
    """Test switching between spaces and persistence."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists("space_settings.json"):
            os.remove("space_settings.json")
        reset_context()

    def test_switch_space_updates_context(self):
        """Test that switch_space updates the application context."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()  # Required by ensure_space_collection

        success = switch_space("new_project")

        assert success is True
        assert ctx.current_space == "new_project"
        assert os.path.exists("space_settings.json")

    def test_save_current_space(self):
        """Test persistence of space settings."""
        ctx = get_context()
        ctx.current_space = "persisted_space"

        save_current_space()

        with open("space_settings.json", "r") as f:
            data = json.load(f)
        assert data["current_space"] == "persisted_space"

    def test_load_current_space(self):
        """Test loading space settings from disk."""
        with open("space_settings.json", "w") as f:
            json.dump({"current_space": "saved_space"}, f)

        loaded = load_current_space()
        assert loaded == "saved_space"

    def test_load_current_space_defaults_to_default(self):
        """Test fallback when no settings file exists."""
        if os.path.exists("space_settings.json"):
            os.remove("space_settings.json")

        assert load_current_space() == "default"

    def test_save_current_space_exception(self):
        """Test exception handling in save_current_space."""
        ctx = get_context()
        ctx.current_space = "test_space"

        with patch("builtins.open", side_effect=Exception("Write error")):
            # Should not raise, just log warning
            save_current_space()  # No assertion, just verifying it doesn't crash

    def test_load_current_space_exception(self):
        """Test exception handling in load_current_space."""
        with open("space_settings.json", "w") as f:
            f.write("invalid json{")

        # Should return default on parse error
        result = load_current_space()
        assert result == "default"


class TestSpaceErrors:
    """Test error handling in space operations."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists("space_settings.json"):
            os.remove("space_settings.json")
        reset_context()

    def test_ensure_space_collection_no_vectorstore(self):
        """Test ensure_space_collection when vectorstore is None."""
        from src.vectordb.spaces import ensure_space_collection

        ctx = get_context()
        ctx.vectorstore = None

        result = ensure_space_collection("test")
        assert result is False

    def test_list_spaces_exception(self):
        """Test list_spaces with client exception."""
        with patch("src.vectordb.spaces.get_chromadb_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.list_collections.side_effect = Exception("Connection error")

            spaces = list_spaces()

            # Should return default on error
            assert spaces == ["default"]

    def test_delete_space_exception(self):
        """Test delete_space with client exception."""
        with patch("src.vectordb.spaces.get_chromadb_client") as mock_get_client:
            mock_client = mock_get_client.return_value
            mock_client.delete_collection.side_effect = Exception("Delete failed")

            result = delete_space("project_x")

            assert result is False

    def test_switch_space_ensure_fails(self):
        """Test switch_space when ensure_space_collection fails."""
        ctx = get_context()
        ctx.vectorstore = None  # This will make ensure_space_collection fail

        result = switch_space("test_space")

        assert result is False
