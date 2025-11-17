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
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Import functions to test - these are the core business logic functions
from main import (  # noqa: F401
    get_space_collection_name,
    ensure_space_collection,
    list_spaces,
    delete_space,
    save_current_space,
    load_current_space,
    switch_space,
    load_embedding_cache,
    load_query_cache,
    save_query_cache,
    cleanup_memory,
    load_memory,
    save_memory,
    get_relevant_context,
    trim_history,
    handle_slash_command,
    show_help,
    handle_clear_command,
    handle_learn_command,
    show_vectordb,
    show_model_info,
    handle_context_command,
    handle_learning_command,
    handle_space_command,
    handle_export_command,
    initialize_application,
)


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

    @patch("main.vectorstore")
    def test_ensure_space_collection_success(self, mock_vectorstore):
        """Test successful space collection ensuring."""
        mock_vectorstore.is_some_value = True
        assert ensure_space_collection("test_space") is True

    @patch("main.vectorstore", None)
    def test_ensure_space_collection_failure(self):
        """Test failed space collection ensuring."""
        result = ensure_space_collection("test_space")
        self.assertFalse(result)


class TestCaching(unittest.TestCase):
    """Test caching functions.

    Tests the performance optimization features:
    - Embedding cache loading and validation
    - Memory cleanup operations
    - Cache persistence across sessions
    """

    @patch("main.os.path.exists")
    @patch("main.open", new_callable=mock_open, read_data='{"test": [1, 2, 3]}')
    @patch("main.json.load")
    def test_load_embedding_cache(self, mock_json_load, mock_file, mock_exists):
        """Test loading embedding cache."""
        mock_exists.return_value = True
        mock_json_load.return_value = {"test": [1, 2, 3]}

        # Reset global cache
        import main

        main.EMBEDDING_CACHE.clear()

        load_embedding_cache()
        assert len(main.EMBEDDING_CACHE) > 0

    def test_cleanup_memory(self):
        """Test memory cleanup function."""
        with patch("gc.collect") as mock_gc:
            cleanup_memory()
            mock_gc.assert_called_once()


class TestMemoryManagement(unittest.TestCase):
    """Test conversation memory management.

    Validates the SQLite-based conversation persistence:
    - Message loading from database with proper type conversion
    - Message saving with thread-safe operations
    - History trimming to prevent memory bloat
    - Database connection handling and error recovery
    """

    @patch("main.DB_TYPE", "sqlite")
    @patch("main.db_conn")
    @patch("main.db_lock")
    def test_load_memory_sqlite(self, mock_lock, mock_conn):
        """Test loading memory from SQLite."""
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("SystemMessage", "Test system message"),
            ("HumanMessage", "Test human message"),
            ("AIMessage", "Test AI message"),
        ]

        messages = load_memory()
        assert len(messages) == 3
        assert isinstance(messages[0], SystemMessage)
        assert isinstance(messages[1], HumanMessage)
        assert isinstance(messages[2], AIMessage)

    @patch("main.DB_TYPE", "sqlite")
    @patch("main.db_conn")
    @patch("main.db_lock")
    def test_save_memory_sqlite(self, mock_lock, mock_conn):
        """Test saving memory to SQLite."""
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        messages = [
            SystemMessage(content="Test system"),
            HumanMessage(content="Test human"),
            AIMessage(content="Test AI"),
        ]

        save_memory(messages)

        # Verify database operations were called
        assert mock_cursor.execute.call_count >= 2  # DELETE and INSERTs
        mock_conn.commit.assert_called_once()

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

    @patch("main.input", return_value="yes")
    @patch("main.conversation_history", [SystemMessage(content="Test")])
    @patch("main.save_memory")
    def test_handle_clear_command_yes(self, mock_save, mock_input):
        """Test /clear command with yes confirmation."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            result = handle_clear_command()
        output = f.getvalue()

        self.assertFalse(result)  # Should not exit
        self.assertIn("cleared", output.lower())

    @patch("main.input", return_value="no")
    def test_handle_clear_command_no(self, mock_input):
        """Test /clear command with no confirmation."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            result = handle_clear_command()
        output = f.getvalue()

        self.assertFalse(result)
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

    @patch("main.list_spaces", return_value=["default", "test"])
    def test_handle_space_command_list(self, mock_list):
        """Test /space list command."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_space_command("list")
        output = f.getvalue()

        self.assertIn("Available spaces", output)

    @patch("main.list_spaces", return_value=["default"])
    @patch("main.switch_space", return_value=True)
    def test_handle_space_command_create(self, mock_switch, mock_list):
        """Test /space create command."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_space_command("create newspace")
        output = f.getvalue()

        self.assertIn("Created and switched", output)

    @patch("main.list_spaces", return_value=["default", "test"])
    @patch("main.switch_space", return_value=True)
    def test_handle_space_command_switch(self, mock_switch, mock_list):
        """Test /space switch command."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_space_command("switch test")
        output = f.getvalue()

        self.assertIn("Switched to space", output)


class TestExportCommand(unittest.TestCase):
    """Test export command functionality."""

    @patch(
        "main.conversation_history",
        [
            SystemMessage(content="System"),
            HumanMessage(content="Human"),
            AIMessage(content="AI"),
        ],
    )
    @patch("builtins.open", new_callable=mock_open)
    def test_handle_export_command_json(self, mock_file):
        """Test /export json command."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_export_command("json")
        output = f.getvalue()

        self.assertIn("exported", output.lower())

    @patch("main.conversation_history", [])
    def test_handle_export_command_empty(self):
        """Test /export command with empty history."""
        import io
        from contextlib import redirect_stdout

        f = io.StringIO()
        with redirect_stdout(f):
            handle_export_command("json")
        output = f.getvalue()

        self.assertIn("No conversation history", output)


class TestInitialization(unittest.TestCase):
    """Test application initialization."""

    @patch("main.ChatOpenAI")
    @patch("chromadb.HttpClient")
    @patch("langchain_ollama.OllamaEmbeddings")
    @patch("langchain_chroma.Chroma")
    @patch("main.sqlite3.connect")
    def test_initialize_application_success(
        self, mock_sqlite, mock_chroma, mock_embeddings, mock_client, mock_llm
    ):
        """Test successful application initialization."""
        # Mock successful initialization
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance

        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance

        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance

        mock_vectorstore_instance = MagicMock()
        mock_chroma.return_value = mock_vectorstore_instance

        mock_conn = MagicMock()
        mock_sqlite.return_value = mock_conn

        with patch.dict(
            "os.environ",
            {
                "LM_STUDIO_URL": "http://test:1234/v1",
                "LM_STUDIO_KEY": "test-key",
                "MODEL_NAME": "test-model",
                "CHROMA_HOST": "localhost",
                "CHROMA_PORT": "8000",
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "EMBEDDING_MODEL": "test-embedding",
                "DB_TYPE": "sqlite",
                "DB_PATH": ":memory:",
                "MAX_HISTORY_PAIRS": "10",
                "TEMPERATURE": "0.7",
                "MAX_INPUT_LENGTH": "1000",
            },
        ):
            result = initialize_application()
            self.assertTrue(result)

    @patch("main.ChatOpenAI", side_effect=Exception("Connection failed"))
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
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
