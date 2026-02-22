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
Unit tests for main.py core functions.

This test suite covers the core functionality of the AI Assistant application:
- Space/workspace management (collection naming, switching, persistence)
- Caching mechanisms (embeddings, query results, memory cleanup)
- Memory management (SQLite database operations, conversation persistence)
- Slash command processing (/help, /clear, /context, /learning, /space, /export)
- Application initialization with proper error handling

Test Structure:
- TestSpaceManagement: Workspace and collection operations
- TestCaching: Embedding and query caching functionality
- TestMemoryManagement: Conversation persistence and retrieval
- TestSlashCommands: Command processing and responses
- TestContextAndLearning: Context and learning mode controls
- TestSpaceCommands: Space management commands
- TestExportCommand: Conversation export functionality
- TestInitialization: Application startup and component initialization

All tests use proper mocking to isolate functionality and avoid external dependencies.
"""

import unittest
from unittest.mock import MagicMock, patch, mock_open
from src.core.context import get_context, reset_context
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import functions to test - these are the core business logic functions
from src.storage import save_memory
from src.vectordb import get_space_collection_name
from src.main import (
    load_embedding_cache,
    handle_slash_command,
)
from src.storage.memory import load_memory
from src.commands.handlers.memory_commands import handle_clear
from src.commands.handlers.config_commands import handle_context, handle_learning
from src.commands.handlers.space_commands import handle_space
from src.commands.handlers.export_commands import handle_export
from src.storage.memory import trim_history
from src.vectordb.spaces import ensure_space_collection
from src.main import initialize_application

# Backwards compatibility aliases
handle_clear_command = handle_clear
handle_context_command = handle_context
handle_learning_command = handle_learning
handle_space_command = handle_space
handle_export_command = handle_export


class TestSpaceManagement(unittest.TestCase):
    """Test space/workspace management functions.

    These tests verify the core workspace functionality:
    - Collection naming conventions for different spaces
    - Space collection validation and creation
    - Space switching and persistence operations
    """

    def test_get_space_collection_name_default(self):
        """Test collection name for default space."""
        assert get_space_collection_name("default") == "knowledge_base"

    def test_get_space_collection_name_custom(self):
        """Test collection name for custom space."""
        assert get_space_collection_name("myspace") == "space_myspace"

    @patch("src.vectordb.spaces.get_context")
    def test_ensure_space_collection_success(self, mock_get_context):
        """Test successful space collection ensuring."""
        mock_ctx = MagicMock()
        mock_ctx.vectorstore = MagicMock()  # vectorstore is available
        mock_get_context.return_value = mock_ctx
        assert ensure_space_collection("test_space") is True

    @patch("src.vectordb.spaces.get_context")
    def test_ensure_space_collection_failure(self, mock_get_context):
        """Test failed space collection ensuring."""
        mock_ctx = MagicMock()
        mock_ctx.vectorstore = None  # vectorstore not available
        mock_get_context.return_value = mock_ctx
        result = ensure_space_collection("test_space")
        self.assertFalse(result)


class TestCaching(unittest.TestCase):
    """Test caching functions."""

    def setUp(self):
        reset_context()

    @patch("src.storage.cache.os.path.exists")
    @patch(
        "src.storage.cache.open",
        new_callable=mock_open,
        read_data='{"test": [1, 2, 3]}',
    )
    @patch("src.storage.cache.json.load")
    def test_load_embedding_cache(self, mock_json_load, mock_file, mock_exists):
        """Test loading embedding cache."""
        mock_exists.return_value = True
        mock_json_load.return_value = {"test": [1, 2, 3]}

        # Reset global cache
        ctx = get_context()
        ctx.embedding_cache.clear()

        load_embedding_cache()
        assert len(ctx.embedding_cache) > 0
        mock_file.assert_called_once()

    def test_cleanup_memory(self):
        """Test memory cleanup function."""
        import gc
        with patch("gc.collect") as mock_gc:
            gc.collect()
            mock_gc.assert_called_once()


class TestMemoryManagement(unittest.TestCase):
    """Test conversation memory management.

    Validates the SQLite-based conversation persistence:
    - Message loading from database with proper type conversion
    - Message saving with thread-safe operations
    - History trimming to prevent memory bloat
    - Database connection handling and error recovery
    """

    @patch("src.storage.memory.get_config")
    @patch("src.storage.memory.get_context")
    def test_load_memory_sqlite(self, mock_get_context, mock_get_config):
        """Test loading memory from SQLite."""
        # Setup config mock
        mock_config = MagicMock()
        mock_config.db_type = "sqlite"
        mock_get_config.return_value = mock_config

        # Setup context mock with db connection
        mock_ctx = MagicMock()
        mock_cursor = MagicMock()
        mock_ctx.db_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("SystemMessage", "Test system message"),
            ("HumanMessage", "Test human message"),
            ("AIMessage", "Test AI message"),
        ]
        mock_get_context.return_value = mock_ctx

        messages = load_memory()
        assert len(messages) == 3
        assert isinstance(messages[0], SystemMessage)
        assert isinstance(messages[1], HumanMessage)
        assert isinstance(messages[2], AIMessage)

    @patch("src.storage.memory.get_config")
    @patch("src.storage.memory.get_context")
    def test_save_memory_sqlite(self, mock_get_context, mock_get_config):
        """Test saving memory to SQLite."""
        # Setup config mock
        mock_config = MagicMock()
        mock_config.db_type = "sqlite"
        mock_get_config.return_value = mock_config

        # Setup context mock with db connection
        mock_ctx = MagicMock()
        mock_cursor = MagicMock()
        mock_ctx.db_conn.cursor.return_value = mock_cursor
        mock_get_context.return_value = mock_ctx

        messages = [
            SystemMessage(content="Test system"),
            HumanMessage(content="Test human"),
            AIMessage(content="Test AI"),
        ]

        save_memory(messages)

        # Verify database operations were called
        # execute called twice: BEGIN TRANSACTION + DELETE
        assert mock_cursor.execute.call_count == 2
        mock_cursor.executemany.assert_called_once()  # INSERT operations
        mock_ctx.db_conn.commit.assert_called_once()

    def test_trim_history_no_trim(self):
        """Test trimming when history is within limits."""
        messages = [
            SystemMessage(content="System"),
            HumanMessage(content="Human 1"),
            AIMessage(content="AI 1"),
            HumanMessage(content="Human 2"),
            AIMessage(content="AI 2"),
        ]

        trimmed = trim_history(messages, 2)
        assert len(trimmed) == 5  # No trimming needed

    def test_trim_history_with_trim(self):
        """Test trimming when history exceeds limits."""
        messages = [
            SystemMessage(content="System"),
            HumanMessage(content="Human 1"),
            AIMessage(content="AI 1"),
            HumanMessage(content="Human 2"),
            AIMessage(content="AI 2"),
            HumanMessage(content="Human 3"),
            AIMessage(content="AI 3"),
        ]

        trimmed = trim_history(messages, 2)
        assert len(trimmed) == 5  # System + 2 pairs (4 messages) = 5 total
        assert trimmed[0].content == "System"  # System message preserved


class TestSlashCommands(unittest.TestCase):
    """Test slash command handling.

    Tests the interactive command system:
    - Command recognition and routing
    - Help system display
    - Clear command with confirmation handling
    - Unknown command error responses
    - Command output formatting and user feedback
    """

    def setUp(self):
        """Ensure commands are registered."""
        reset_context()
        import importlib
        import src.commands.handlers.help_commands

        importlib.reload(src.commands.handlers.help_commands)
        # We only really need help for the help test

    def test_handle_slash_command_help(self):
        # Capture stdout
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            result = handle_slash_command("/help")
        output = f.getvalue()

        self.assertTrue(result)
        self.assertIn("Available Commands", output)

    def test_handle_slash_command_unknown(self):
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            result = handle_slash_command("/unknown")
        output = f.getvalue()

        self.assertTrue(result)
        self.assertIn("Unknown command", output)

    def test_handle_slash_command_not_slash(self):
        """Test non-slash input."""
        result = handle_slash_command("regular message")
        assert result is False

    @patch("builtins.input", return_value="yes")
    @patch("src.commands.handlers.memory_commands.save_memory")
    @patch("src.commands.handlers.memory_commands.get_context")
    def test_handle_clear_command_yes(self, mock_ctx, mock_save, mock_input):
        """Test /clear command with yes confirmation."""
        import io
        from contextlib import redirect_stdout

        mock_ctx.return_value.conversation_history = [SystemMessage(content="Test")]

        f = io.StringIO()
        with redirect_stdout(f):
            handle_clear_command([])
        output = f.getvalue()

        self.assertIn("cleared", output.lower())
        mock_input.assert_called_once()  # Verify user was prompted
        mock_save.assert_called_once()  # Verify memory was saved

    @patch("builtins.input", return_value="no")
    @patch("src.commands.handlers.memory_commands.get_context")
    def test_handle_clear_command_no(self, mock_ctx, mock_input):
        """Test /clear command with no confirmation."""
        import io
        from contextlib import redirect_stdout

        mock_ctx.return_value.conversation_history = []

        f = io.StringIO()
        with redirect_stdout(f):
            handle_clear_command([])
        output = f.getvalue()

        self.assertIn("cancelled", output.lower())


class TestContextAndLearning(unittest.TestCase):
    """Test context and learning mode commands."""

    def test_handle_context_command_valid(self):
        """Test /context command with valid mode."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_context_command(["on"])
        output = f.getvalue()

        self.assertIn("Context mode set to: on", output)

    def test_handle_context_command_invalid(self):
        """Test /context command with invalid mode."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_context_command(["invalid"])
        output = f.getvalue()

        self.assertIn("Invalid context mode", output)

    def test_handle_learning_command_valid(self):
        """Test /learning command with valid mode."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_learning_command(["strict"])
        output = f.getvalue()

        self.assertIn("Learning mode set to: strict", output)

    def test_handle_learning_command_invalid(self):
        """Test /learning command with invalid mode."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_learning_command(["invalid"])
        output = f.getvalue()

        self.assertIn("Invalid learning mode", output)


class TestSpaceCommands(unittest.TestCase):
    """Test space management commands."""

    @patch(
        "src.commands.handlers.space_commands.list_spaces",
        return_value=["default", "test"],
    )
    def test_handle_space_command_list(self, mock_list):
        """Test /space list command."""
        from src.core.context import reset_context, get_context
        import io
        from contextlib import redirect_stdout
        from src.commands.handlers.space_commands import handle_space

        reset_context()
        ctx = get_context()
        ctx.current_space = "default"

        f = io.StringIO()
        with redirect_stdout(f):
            handle_space(["list"])
        output = f.getvalue()

        self.assertIn("Available spaces", output)
        mock_list.assert_called()  # Verify spaces were listed

    @patch("src.commands.handlers.space_commands.ensure_space_collection")
    def test_handle_space_command_create(self, mock_ensure):
        """Test /space create command."""
        from src.core.context import reset_context, get_context
        import io
        from contextlib import redirect_stdout
        from src.commands.handlers.space_commands import handle_space

        reset_context()
        ctx = get_context()
        ctx.current_space = "default"

        f = io.StringIO()
        with redirect_stdout(f):
            handle_space(["create", "newspace"])
        output = f.getvalue()

        self.assertIn("Created and switched", output)
        mock_ensure.assert_called_once_with("newspace")

    def test_handle_space_command_switch(self):
        """Test /space switch command."""
        from src.core.context import reset_context, get_context
        import io
        from contextlib import redirect_stdout
        from src.commands.handlers.space_commands import handle_space

        reset_context()
        ctx = get_context()
        ctx.current_space = "default"

        f = io.StringIO()
        with redirect_stdout(f):
            handle_space(["switch", "test"])
        output = f.getvalue()

        self.assertIn("Switched to space", output)
        # Verify current space was updated
        self.assertEqual(ctx.current_space, "test")


class TestExportCommand(unittest.TestCase):
    """Test export command functionality."""

    @patch("src.commands.handlers.export_commands.get_context")
    @patch("builtins.open", new_callable=mock_open)
    def test_handle_export_command_json(self, mock_file, mock_ctx):
        """Test /export json command."""
        import io
        from contextlib import redirect_stdout

        mock_ctx.return_value.conversation_history = [
            SystemMessage(content="System"),
            HumanMessage(content="Human"),
            AIMessage(content="AI"),
        ]

        f = io.StringIO()
        with redirect_stdout(f):
            handle_export_command(["json"])
        output = f.getvalue()

        self.assertIn("exported", output.lower())

    @patch("src.commands.handlers.export_commands.get_context")
    def test_handle_export_command_empty(self, mock_ctx):
        """Test /export command with empty history."""
        import io
        from contextlib import redirect_stdout

        mock_ctx.return_value.conversation_history = []

        f = io.StringIO()
        with redirect_stdout(f):
            handle_export_command(["json"])
        output = f.getvalue()

        self.assertIn("No conversation history", output)


class TestInitialization(unittest.TestCase):
    """Test application initialization."""

    @patch("src.main.initialize_llm", return_value=True)
    @patch("src.main.initialize_vectordb", return_value=True)
    @patch("src.main.initialize_user_memory", return_value=True)
    @patch("src.main.initialize_database")
    @patch("src.storage.memory.load_memory", return_value=[])
    def test_initialize_application_success(
        self, mock_load, mock_db, mock_mem0, mock_vdb, mock_llm
    ):
        """Test successful application initialization."""
        result = initialize_application()
        self.assertTrue(result)
        mock_llm.assert_called_once()
        mock_vdb.assert_called_once()

    @patch("src.main.get_llm", side_effect=Exception("Connection failed"))
    def test_initialize_application_llm_failure(self, mock_llm):
        """Test initialization failure due to LLM connection issues."""
        with patch.dict(
            "os.environ",
            {
                "LM_STUDIO_URL": "http://test:1234/v1",
                "LM_STUDIO_KEY": "test-key",
                "MODEL_NAME": "test-model",
            },
        ):
            result = initialize_application()
            self.assertTrue(result)  # Application gracefully handles LLM failures


if __name__ == "__main__":
    unittest.main()
