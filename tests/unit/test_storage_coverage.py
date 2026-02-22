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
Unit tests targeting coverage gaps in src/storage/database.py and src/storage/memory.py.
"""

import sqlite3
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage

from src.storage.database import initialize_database
from src.storage.memory import load_memory, save_memory
from src.core.context import get_context, reset_context


class TestDatabaseCoverage:
    """Test coverage gaps in database.py."""

    def setup_method(self):
        reset_context()

    @patch("src.storage.database.sqlite3.connect")
    def test_initialize_database_failure(self, mock_connect):
        """Test database initialization failure handling."""
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        conn, lock = initialize_database()

        assert conn is None
        assert lock is None


class TestMemoryCoverage:
    """Test coverage gaps in memory.py."""

    def setup_method(self):
        reset_context()

    def test_load_memory_unknown_message_type(self):
        """Test loading unknown message types from DB."""
        # Setup context with mock DB
        ctx = get_context()
        mock_conn = Mock()
        mock_cursor = Mock()

        # Return a row with unknown type "UnknownType"
        mock_cursor.fetchall.return_value = [("UnknownType", "content")]
        mock_conn.cursor.return_value = mock_cursor

        ctx.db_conn = mock_conn
        ctx.db_lock = Mock()

        # Mock config to enable sqlite
        with patch("src.storage.memory.get_config") as mock_config_get:
            mock_config = Mock()
            mock_config.db_type = "sqlite"
            mock_config_get.return_value = mock_config

            history = load_memory()

            # Should skip the unknown message
            assert len(history) == 0

    def test_load_memory_general_exception(self):
        """Test handling of general exceptions during load."""
        ctx = get_context()
        mock_conn = Mock()
        # Raise exception when getting cursor
        mock_conn.cursor.side_effect = Exception("DB Error")

        ctx.db_conn = mock_conn
        ctx.db_lock = Mock()

        with patch("src.storage.memory.get_config") as mock_config_get:
            mock_config = Mock()
            mock_config.db_type = "sqlite"
            mock_config_get.return_value = mock_config

            history = load_memory()

            # Should recover and return empty list
            assert history == []

    def test_save_memory_db_missing(self):
        """Test saving when DB is missing (RuntimeError pathway)."""
        ctx = get_context()
        ctx.db_conn = None  # Ensure no DB

        with patch("src.storage.memory.get_config") as mock_config_get:
            mock_config = Mock()
            mock_config.db_type = "sqlite"
            mock_config_get.return_value = mock_config

            with pytest.raises(
                RuntimeError, match="Database required but not available"
            ):
                save_memory([HumanMessage(content="hi")])

    def test_save_memory_exception_reraise(self):
        """Test that exceptions during save are re-raised."""
        ctx = get_context()
        mock_conn = Mock()
        mock_cursor = Mock()
        # Raise error on execute
        mock_cursor.execute.side_effect = Exception("Insert failed")
        mock_conn.cursor.return_value = mock_cursor

        ctx.db_conn = mock_conn
        ctx.db_lock = MagicMock()  # Needs to be a context manager

        with patch("src.storage.memory.get_config") as mock_config_get:
            mock_config = Mock()
            mock_config.db_type = "sqlite"
            mock_config_get.return_value = mock_config

            with pytest.raises(Exception, match="Insert failed"):
                save_memory([HumanMessage(content="hi")])
