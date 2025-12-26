#!/usr/bin/env python3
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
Test suite for Memory Module (src/storage/memory.py).

Tests cover:
- Loading memory from database
- Saving memory to database
- History trimming logic
- Message reconstruction from database rows
"""

from unittest.mock import patch, MagicMock
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.storage.memory import load_memory, save_memory, trim_history
from src.core.context import get_context, reset_context


class TestConversationPersistence:
    """Test loading and saving conversation history."""

    def setup_method(self):
        """Set up test environment."""
        reset_context()

    def teardown_method(self):
        """Clean up test environment."""
        reset_context()

    def test_load_memory_empty_db(self):
        """Test loading memory when the database is empty."""
        ctx = get_context()
        ctx.db_conn = MagicMock()
        ctx.db_lock = MagicMock()

        # Mock cursor to return no rows
        mock_cursor = ctx.db_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []

        with patch("src.core.config.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_get_config.return_value = mock_config

            history = load_memory()

            assert len(history) == 1
            assert isinstance(history[0], SystemMessage)
            assert "coding" in history[0].content

    def test_load_memory_with_data(self):
        """Test loading and reconstructing messages from the database."""
        ctx = get_context()
        ctx.db_conn = MagicMock()
        ctx.db_lock = MagicMock()

        # Mock data from DB
        rows = [
            ("SystemMessage", "Sys prompt"),
            ("HumanMessage", "Hello"),
            ("AIMessage", "Hi there"),
        ]

        mock_cursor = ctx.db_conn.cursor.return_value
        mock_cursor.fetchall.return_value = rows

        with patch("src.core.config.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_get_config.return_value = mock_config

            history = load_memory()

            assert len(history) == 3
            assert isinstance(history[0], SystemMessage)
            assert isinstance(history[1], HumanMessage)
            assert isinstance(history[2], AIMessage)
            assert history[1].content == "Hello"

    def test_load_memory_no_db(self):
        """Test loading memory when the database is not available."""
        ctx = get_context()
        ctx.db_conn = None  # No connection

        with patch("src.core.config.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_get_config.return_value = mock_config

            history = load_memory()
            assert history == []

    def test_save_memory(self):
        """Test saving memory to the database."""
        ctx = get_context()
        ctx.db_conn = MagicMock()
        ctx.db_lock = MagicMock()
        mock_cursor = ctx.db_conn.cursor.return_value

        history = [SystemMessage(content="Sys"), HumanMessage(content="User")]

        with patch("src.core.config.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.db_type = "sqlite"
            mock_get_config.return_value = mock_config

            save_memory(history)

            # Verify existing messages were deleted
            mock_cursor.execute.assert_any_call(
                "DELETE FROM conversations WHERE session_id = 'default'"
            )

            # Verify bulk insert was called
            assert mock_cursor.executemany.called
            args = mock_cursor.executemany.call_args[0]
            assert len(args[1]) == 2
            assert args[1][1] == ("default", "HumanMessage", "User")

            # Verify commit
            assert ctx.db_conn.commit.called


class TestHistoryTrimming:
    """Test the logic for trimming conversation history."""

    def test_trim_history_no_trim_needed(self):
        """Test that history is not trimmed if it's within limits."""
        history = [
            SystemMessage(content="S"),
            HumanMessage(content="H"),
            AIMessage(content="A"),
        ]

        # Limit is 2 pairs (total 5 msgs)
        trimmed = trim_history(history, max_pairs=2)

        assert len(trimmed) == 3
        assert trimmed == history

    def test_trim_history_performs_trim(self):
        """Test that history is trimmed correctly to keep system msg + recent pairs."""
        history = [
            SystemMessage(content="System"),  # Always keep
            HumanMessage(content="H1"),
            AIMessage(content="A1"),
            HumanMessage(content="H2"),
            AIMessage(content="A2"),
            HumanMessage(content="H3"),
            AIMessage(content="A3"),
        ]

        # Limit to 1 pair (total 1 + 2 = 3 msgs)
        trimmed = trim_history(history, max_pairs=1)

        assert len(trimmed) == 3
        assert trimmed[0].content == "System"
        assert trimmed[1].content == "H3"
        assert trimmed[2].content == "A3"

    def test_trim_history_uses_config_default(self):
        """Test that trim_history uses the default limit from config."""
        history = [SystemMessage(content="S")] + [HumanMessage(content="H")] * 20

        with patch("src.storage.memory.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.max_history_pairs = 5
            mock_get_config.return_value = mock_config

            trimmed = trim_history(history)
            # 1 (sys) + 5*2 (pairs) = 11
            assert len(trimmed) == 11
            assert trimmed[0].content == "S"
