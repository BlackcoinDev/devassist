#!/usr/bin/env python3
"""
Test suite for Command Handlers (src/commands/handlers/*.py).

Tests cover:
- /context and /learning (config_commands.py)
- /help and /model (help_commands.py)
- /space (space_commands.py)
- Input validation and output formatting
"""

from unittest.mock import Mock, patch, MagicMock
from src.commands.handlers.config_commands import handle_context, handle_learning
from src.commands.handlers.help_commands import handle_help, handle_model_info
from src.commands.handlers.space_commands import handle_space
from src.commands.handlers.database_commands import handle_vectordb
from src.commands.handlers.learning_commands import handle_learn
from src.commands.handlers.memory_commands import handle_memory, handle_clear
from src.commands.handlers.file_commands import handle_read, handle_write
from src.commands.handlers.export_commands import handle_export
from src.core.context import get_context, reset_context
from langchain_core.messages import HumanMessage


class TestConfigHandlers:
    """Test configuration command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_context_show(self, mock_print):
        """Test showing current context mode."""
        ctx = get_context()
        ctx.context_mode = "auto"

        handle_context([])

        # Verify it printed the current mode
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current context mode: auto" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.config_commands.set_context_mode')
    def test_handle_context_set(self, mock_set, mock_print):
        """Test setting context mode."""
        handle_context(["on"])
        mock_set.assert_called_with("on")

        # Test invalid mode
        handle_context(["invalid"])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Invalid context mode" in output

    @patch('builtins.print')
    def test_handle_learning_show(self, mock_print):
        """Test showing current learning mode."""
        ctx = get_context()
        ctx.learning_mode = "normal"

        handle_learning([])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current learning mode: normal" in output


class TestHelpHandlers:
    """Test help and information command handlers."""

    @patch('builtins.print')
    def test_handle_help(self, mock_print):
        """Test that help menu displays."""
        handle_help([])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Available Commands" in output
        assert "/memory" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.help_commands.get_config')
    def test_handle_model_info(self, mock_get_config, mock_print):
        """Test displaying model information."""
        mock_config = MagicMock()
        mock_config.model_name = "test-model"
        mock_config.lm_studio_url = "http://localhost:1234/v1"
        mock_config.temperature = 0.7
        mock_get_config.return_value = mock_config

        handle_model_info([])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current Model: test-model" in output
        assert "Temperature: 0.7" in output


class TestSpaceHandlers:
    """Test space management command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_space_show_current(self, mock_print):
        """Test showing current space info."""
        ctx = get_context()
        ctx.current_space = "my-space"

        handle_space([])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current space: my-space" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.space_commands.list_spaces')
    def test_handle_space_list(self, mock_list_spaces, mock_print):
        """Test listing available spaces."""
        mock_list_spaces.return_value = ["default", "work", "personal"]

        handle_space(["list"])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Available spaces (3):" in output
        assert "work" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.space_commands.switch_space')
    @patch('src.commands.handlers.space_commands.list_spaces')
    def test_handle_space_create(self, mock_list, mock_switch, mock_print):
        """Test creating a new space."""
        mock_list.return_value = ["default"]
        mock_switch.return_value = True

        handle_space(["create", "new-project"])

        mock_switch.assert_called_with("new-project")
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Created and switched to space: new-project" in output

    @patch('builtins.print')
    @patch('builtins.input', return_value="yes")
    @patch('src.commands.handlers.space_commands.delete_space')
    @patch('src.commands.handlers.space_commands.list_spaces')
    def test_handle_space_delete(self, mock_list, mock_delete, mock_input, mock_print):
        """Test deleting an existing space with confirmation."""
        mock_list.return_value = ["default", "old-space"]
        mock_delete.return_value = True

        handle_space(["delete", "old-space"])

        mock_delete.assert_called_with("old-space")
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Deleted space: old-space" in output


class TestDatabaseHandlers:
    """Test database related command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    @patch('src.commands.handlers.database_commands._get_api_session')
    @patch('src.commands.handlers.database_commands.get_config')
    def test_handle_vectordb_success(self, mock_get_config, mock_session, mock_print):
        """Test displaying vector database stats."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        ctx.current_space = "default"

        mock_config = MagicMock()
        mock_config.chroma_host = "localhost"
        mock_config.chroma_port = 8000
        mock_get_config.return_value = mock_config

        # Mock API responses
        mock_api = mock_session.return_value
        mock_api.get.side_effect = [
            MagicMock(status_code=200, json=lambda: [{"id": "id1", "name": "knowledge_base"}]),  # list colls
            MagicMock(status_code=200, json=lambda: 42)  # count
        ]

        handle_vectordb([])

        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Chunks: 42" in output


class TestLearningHandlers:
    """Test learning command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    @patch('src.commands.handlers.learning_commands.add_to_knowledge_base')
    def test_handle_learn_success(self, mock_add, mock_print):
        """Test the /learn command."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        mock_add.return_value = True

        handle_learn(["some", "new", "fact"])

        mock_add.assert_called_with("some new fact")
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Learned: some new fact" in output

    @patch('builtins.print')
    def test_handle_learn_no_args(self, mock_print):
        """Test /learn without arguments."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        handle_learn([])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Usage: /learn" in output


class TestMemoryHandlers:
    """Test memory management command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_memory(self, mock_print):
        """Test displaying conversation history."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Hello world")]

        handle_memory([])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Conversation History (1 messages)" in output
        assert "Hello world" in output

    @patch('builtins.print')
    @patch('builtins.input', return_value="yes")
    @patch('src.commands.handlers.memory_commands.save_memory')
    def test_handle_clear(self, mock_save, mock_input, mock_print):
        """Test clearing memory."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Bye")]

        handle_clear([])

        assert len(ctx.conversation_history) == 1
        assert "coding" in ctx.conversation_history[0].content  # New system message
        assert mock_save.called


class TestFileHandlers:
    """Test file operation command handlers."""

    @patch('builtins.print')
    @patch('os.getcwd', return_value="/mock/dir")
    @patch('os.path.abspath', side_effect=lambda x: f"/mock/dir/{x}")
    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.getsize', return_value=100)
    def test_handle_read_success(self, mock_size, mock_isfile, mock_exists, mock_abs, mock_cwd, mock_print):
        """Test reading a file securely."""
        with patch('builtins.open', MagicMock(return_value=MagicMock(__enter__=lambda x: MagicMock(read=lambda: "file context")))):
            handle_read(["test.txt"])
            output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
            assert "file context" in output

    @patch('builtins.print')
    @patch('os.getcwd', return_value="/mock/dir")
    @patch('os.path.abspath', side_effect=lambda x: f"/mock/dir/{x}")
    @patch('os.path.exists', return_value=True)
    def test_handle_write_success(self, mock_exists, mock_abs, mock_cwd, mock_print):
        """Test writing to a file securely."""
        with patch('builtins.open', MagicMock()) as mock_open:
            handle_write(["test.txt", "hello", "world"])

            mock_open.assert_called_with("/mock/dir/test.txt", "w", encoding="utf-8")
            output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
            assert "File written: test.txt" in output


class TestExportHandlers:
    """Test conversation export command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_export_no_history(self, mock_print):
        """Test export when history is empty."""
        ctx = get_context()
        ctx.conversation_history = []
        handle_export(["json"])
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "No conversation history to export" in output

    @patch('builtins.print')
    def test_handle_export_json_success(self, mock_print):
        """Test successful JSON export."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Save me")]

        with patch('builtins.open', MagicMock()):
            handle_export(["json"])
            output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
            assert "Conversation exported to:" in output
            assert "Format: JSON" in output
