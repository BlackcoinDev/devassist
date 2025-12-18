#!/usr/bin/env python3
"""
Test suite for Legacy Command Handlers (src/commands/handlers/legacy_commands.py).

Tests cover all legacy slash commands that haven't been migrated to the new system yet.
"""

import pytest
import io
import sys
from unittest.mock import Mock, patch, MagicMock
from src.commands.handlers.legacy_commands import (
    handle_read_command, handle_write_command, handle_list_command, handle_pwd_command,
    show_memory, handle_clear_command, handle_learn_command, show_vectordb, show_mem0,
    handle_populate_command, show_model_info, handle_context_command, handle_learning_command,
    handle_space_command, handle_export_command
)
from src.core.context import get_context, reset_context
from langchain_core.messages import HumanMessage, SystemMessage


class TestLegacyFileHandlers:
    """Test legacy file operation command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_read_file')
    def test_handle_read_command_success(self, mock_execute, mock_print):
        """Test reading a file successfully."""
        mock_execute.return_value = {
            "content": "Hello World\nLine 2",
            "file_info": {
                "name": "test.txt",
                "size": 18,
                "lines": 2,
                "type": "text/plain"
            }
        }
        
        handle_read_command("test.txt")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Hello World" in output
        assert "Line 2" in output
        assert "1: Hello World" in output
        assert "2: Line 2" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_read_file')
    def test_handle_read_command_error(self, mock_execute, mock_print):
        """Test reading a file with error."""
        mock_execute.return_value = {"error": "File not found"}
        
        handle_read_command("nonexistent.txt")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Error reading file: File not found" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_read_file')
    def test_handle_read_command_no_file_path(self, mock_execute, mock_print):
        """Test reading with no file path."""
        handle_read_command("")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Please specify a file path" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_write_file')
    def test_handle_write_command_success(self, mock_execute, mock_print):
        """Test writing to a file successfully."""
        mock_execute.return_value = {"success": True}
        
        handle_write_command("test.txt:Hello World")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "File 'test.txt' written successfully" in output
        assert "Wrote 11 characters" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_write_file')
    def test_handle_write_command_error(self, mock_execute, mock_print):
        """Test writing to a file with error."""
        mock_execute.return_value = {"success": False, "error": "Permission denied"}
        
        handle_write_command("test.txt:Hello World")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Error writing file" in output
        assert "Permission denied" in output

    @patch('builtins.print')
    def test_handle_write_command_empty_content(self, mock_print):
        """Test writing with empty content."""
        handle_write_command("test.txt:")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Both filename and content are required" in output

    @patch('builtins.print')
    def test_handle_write_command_invalid_format(self, mock_print):
        """Test writing with invalid format."""
        handle_write_command("test.txt")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Usage: /write filename:content" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_list_directory')
    def test_handle_list_command_success(self, mock_execute, mock_print):
        """Test listing directory contents."""
        mock_execute.return_value = {
            "items": [
                {"name": "subdir", "type": "directory", "size": 4096},
                {"name": "file1.txt", "type": "file", "size": 100},
                {"name": "file2.py", "type": "file", "size": 200}
            ],
            "path": "."
        }
        
        handle_list_command("")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Contents of '.'" in output
        assert "subdir/" in output
        assert "file1.txt" in output
        assert "file2.py" in output
        assert "Total: 1 directories, 2 files" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_list_directory')
    def test_handle_list_command_error(self, mock_execute, mock_print):
        """Test listing directory with error."""
        mock_execute.return_value = {"error": "Directory not found"}
        
        handle_list_command("nonexistent")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Error:" in output
        assert "Directory not found" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_list_directory')
    def test_handle_list_command_empty(self, mock_execute, mock_print):
        """Test listing empty directory."""
        mock_execute.return_value = {
            "items": [],
            "path": "/empty/dir"
        }
        
        handle_list_command("/empty/dir")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Directory '/empty/dir' is empty" in output

    @patch('builtins.print')
    @patch('os.getcwd', return_value="/test/dir")
    def test_handle_pwd_command(self, mock_cwd, mock_print):
        """Test showing current directory."""
        handle_pwd_command()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current directory: /test/dir" in output


class TestLegacyMemoryHandlers:
    """Test legacy memory management command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_show_memory_empty(self, mock_print):
        """Test showing empty memory."""
        ctx = get_context()
        ctx.conversation_history = []
        
        show_memory()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "No conversation history available" in output

    @patch('builtins.print')
    def test_show_memory_with_content(self, mock_print):
        """Test showing memory with conversation history."""
        ctx = get_context()
        ctx.conversation_history = [
            HumanMessage(content="Hello there!"),
            SystemMessage(content="Welcome to the system")
        ]
        
        show_memory()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Conversation History (2 messages)" in output
        assert "Hello there!" in output
        assert "Welcome to the system" in output

    @patch('builtins.print')
    @patch('builtins.input', return_value="yes")
    @patch('src.commands.handlers.legacy_commands.save_memory')
    def test_handle_clear_command_confirmed(self, mock_save, mock_input, mock_print):
        """Test clearing memory with confirmation."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Old message")]
        
        result = handle_clear_command()
        
        assert result is True
        assert len(ctx.conversation_history) == 1
        assert isinstance(ctx.conversation_history[0], SystemMessage)
        assert "coding" in ctx.conversation_history[0].content
        mock_save.assert_called_once()

    @patch('builtins.print')
    @patch('builtins.input', return_value="no")
    def test_handle_clear_command_cancelled(self, mock_input, mock_print):
        """Test clearing memory cancelled."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Old message")]
        
        result = handle_clear_command()
        
        assert result is False
        assert len(ctx.conversation_history) == 1
        assert "Old message" in ctx.conversation_history[0].content


class TestLegacyLearningHandlers:
    """Test legacy learning command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.execute_learn_information')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_learn_command_success(self, mock_config, mock_execute, mock_print):
        """Test learning new information successfully."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        mock_config.return_value.current_space = "test-space"
        mock_execute.return_value = {"success": True}
        
        handle_learn_command("Python is awesome")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Learned: Python is awesome" in output
        assert "Added to knowledge base" in output

    @patch('builtins.print')
    def test_handle_learn_command_no_content(self, mock_print):
        """Test learning with no content."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        handle_learn_command("")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Please provide content to learn" in output

    @patch('builtins.print')
    def test_handle_learn_command_no_vectorstore(self, mock_print):
        """Test learning when vectorstore is not available."""
        ctx = get_context()
        ctx.vectorstore = None
        
        handle_learn_command("Some content")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Vector database not available" in output


class TestLegacyVectorDBHandlers:
    """Test legacy vector database command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_show_vectordb_no_connection(self, mock_print):
        """Test showing vector DB when not connected."""
        ctx = get_context()
        ctx.vectorstore = None
        
        show_vectordb()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Vector database not connected" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_space_collection_name')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_show_vectordb_empty(self, mock_config, mock_collection_name, mock_print):
        """Test showing empty vector DB."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        mock_config.return_value.current_space = "test-space"
        mock_collection_name.return_value = "test_collection"
        
        # Mock collection that returns None
        ctx.vectorstore.get_collection.return_value = None
        
        show_vectordb()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "has no knowledge base yet" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_space_collection_name')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_show_mem0_no_memory(self, mock_config, mock_collection_name, mock_print):
        """Test showing Mem0 when not available."""
        ctx = get_context()
        ctx.user_memory = None
        
        show_mem0()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Mem0 not available" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_show_mem0_empty(self, mock_config, mock_print):
        """Test showing empty Mem0."""
        ctx = get_context()
        ctx.user_memory = MagicMock()
        ctx.user_memory.get_all.return_value = {"results": []}
        
        mock_config.return_value.verbose_logging = False
        
        show_mem0()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "No personalized memories stored yet" in output


class TestLegacyPopulateHandlers:
    """Test legacy populate command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_populate_no_vectorstore(self, mock_print):
        """Test populate when vectorstore is not available."""
        ctx = get_context()
        ctx.vectorstore = None
        
        handle_populate_command("test_dir")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Vector database not available" in output

    @patch('builtins.print')
    def test_handle_populate_no_directory(self, mock_print):
        """Test populate with no directory specified."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        handle_populate_command("")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Please specify a directory" in output

    @patch('builtins.print')
    @patch('os.path.abspath', return_value="/test/dir")
    @patch('os.path.isdir', return_value=False)
    def test_handle_populate_directory_not_found(self, mock_isdir, mock_abspath, mock_print):
        """Test populate with non-existent directory."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        handle_populate_command("nonexistent")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Directory not found" in output

    @patch('builtins.print')
    @patch('os.path.abspath', return_value="/test/dir")
    @patch('os.path.isdir', return_value=True)
    @patch('os.walk')
    def test_handle_populate_no_supported_files(self, mock_walk, mock_isdir, mock_abspath, mock_print):
        """Test populate with directory containing no supported files."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        # Mock os.walk to return no files
        mock_walk.return_value = [("/test/dir", [], [])]
        
        handle_populate_command("/test/dir")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "No supported files found" in output

    @patch('builtins.print')
    @patch('os.path.abspath', return_value="/test/dir")
    @patch('os.path.isdir', return_value=True)
    @patch('os.walk')
    @patch('src.commands.handlers.legacy_commands.execute_parse_document')
    @patch('src.commands.handlers.legacy_commands.execute_learn_information')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_populate_success(self, mock_config, mock_learn, mock_parse, mock_walk, mock_isdir, mock_abspath, mock_print):
        """Test successful populate operation."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        mock_config.return_value.current_space = "test-space"
        
        # Mock os.walk to return some files
        mock_walk.return_value = [
            ("/test/dir", [], ["test.txt", "test.py"])
        ]
        
        # Mock parse and learn operations
        mock_parse.return_value = {"success": True, "content": "This is a much longer test content that should be more than 50 characters long to pass the minimum content threshold for processing."}
        mock_learn.return_value = {"success": True}
        
        handle_populate_command("/test/dir")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Population complete" in output
        assert "Processed: 2 files" in output

    @patch('builtins.print')
    @patch('os.path.abspath', return_value="/test/dir")
    @patch('os.path.isdir', return_value=True)
    @patch('os.walk')
    @patch('src.commands.handlers.legacy_commands.execute_parse_document')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_populate_parse_error(self, mock_config, mock_parse, mock_walk, mock_isdir, mock_abspath, mock_print):
        """Test populate with parse error."""
        ctx = get_context()
        ctx.vectorstore = MagicMock()
        
        mock_config.return_value.current_space = "test-space"
        
        # Mock os.walk to return some files
        mock_walk.return_value = [
            ("/test/dir", [], ["test.txt"])
        ]
        
        # Mock parse operation to fail
        mock_parse.side_effect = Exception("Parse error")
        
        handle_populate_command("/test/dir")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Error processing test.txt" in output
        assert "Parse error" in output


class TestLegacyModelHandlers:
    """Test legacy model information command handlers."""

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_context')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_show_model_info(self, mock_config, mock_context, mock_print):
        """Test showing model information."""
        mock_config.return_value.model_name = "test-model"
        mock_config.return_value.lm_studio_url = "http://localhost:1234"
        mock_config.return_value.temperature = 0.7
        mock_config.return_value.max_tokens = 1000
        
        mock_context.return_value.llm = MagicMock()
        
        show_model_info()
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Model: test-model" in output
        assert "API: http://localhost:1234" in output
        assert "Temperature: 0.7" in output
        assert "Max Tokens: 1000" in output
        assert "Connected to: test-model" in output


class TestLegacyContextHandlers:
    """Test legacy context command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_context_command_show(self, mock_config, mock_print):
        """Test showing current context mode."""
        mock_config.return_value.context_mode = "auto"
        
        handle_context_command([])
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current context mode: auto" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_context_command_set(self, mock_config, mock_print):
        """Test setting context mode."""
        mock_config.return_value.context_mode = "auto"
        
        handle_context_command(["on"])
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Context mode set to: on" in output
        assert mock_config.return_value.context_mode == "on"

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_context_command_invalid(self, mock_config, mock_print):
        """Test setting invalid context mode."""
        mock_config.return_value.context_mode = "auto"
        
        handle_context_command(["invalid"])
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Invalid mode: invalid" in output


class TestLegacyLearningModeHandlers:
    """Test legacy learning mode command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_learning_command_show(self, mock_config, mock_print):
        """Test showing current learning mode."""
        mock_config.return_value.learning_mode = "normal"
        
        handle_learning_command([])
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Current learning mode: normal" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_learning_command_set(self, mock_config, mock_print):
        """Test setting learning mode."""
        mock_config.return_value.learning_mode = "normal"
        
        handle_learning_command(["strict"])
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Learning mode set to: strict" in output
        assert mock_config.return_value.learning_mode == "strict"

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_learning_command_invalid(self, mock_config, mock_print):
        """Test setting invalid learning mode."""
        mock_config.return_value.learning_mode = "normal"
        
        handle_learning_command(["invalid"])
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Invalid mode: invalid" in output


class TestLegacySpaceHandlers:
    """Test legacy space command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_space_command_no_args(self, mock_print):
        """Test space command with no arguments."""
        handle_space_command("")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Please specify a space command" in output

    @patch('builtins.print')
    @patch('src.vectordb.list_spaces')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_space_command_list(self, mock_config, mock_list_spaces, mock_print):
        """Test listing spaces."""
        mock_config.return_value.current_space = "default"
        mock_list_spaces.return_value = ["default", "work", "personal"]
        
        handle_space_command("list")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Knowledge Spaces (3)" in output
        assert "✅ default" in output
        assert "work" in output
        assert "personal" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.ensure_space_collection')
    def test_handle_space_command_create(self, mock_ensure, mock_print):
        """Test creating a new space."""
        handle_space_command("create new-space")
        
        mock_ensure.assert_called_with("new-space")
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Created space: new-space" in output

    @patch('builtins.print')
    @patch('src.vectordb.switch_space')
    @patch('src.vectordb.save_current_space')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_space_command_switch(self, mock_config, mock_save, mock_switch, mock_print):
        """Test switching to a space."""
        mock_config.return_value.current_space = "default"
        mock_switch.return_value = True
        
        handle_space_command("switch work")
        
        mock_switch.assert_called_with("work")
        mock_save.assert_called_with("work")
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Switched to space: work" in output

    @patch('builtins.print')
    @patch('src.vectordb.delete_space')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_space_command_delete(self, mock_config, mock_delete, mock_print):
        """Test deleting a space."""
        mock_config.return_value.current_space = "default"
        mock_delete.return_value = True
        
        handle_space_command("delete old-space")
        
        mock_delete.assert_called_with("old-space")
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Deleted space: old-space" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_space_command_delete_default(self, mock_config, mock_print):
        """Test deleting default space (should fail)."""
        mock_config.return_value.current_space = "default"
        
        handle_space_command("delete default")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Cannot delete the default space" in output

    @patch('builtins.print')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_space_command_delete_current(self, mock_config, mock_print):
        """Test deleting current space (should fail)."""
        mock_config.return_value.current_space = "work"
        
        handle_space_command("delete work")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Cannot delete the current space" in output

    @patch('builtins.print')
    @patch('src.vectordb.delete_space')
    @patch('src.commands.handlers.legacy_commands.get_config')
    def test_handle_space_command_delete_failure(self, mock_config, mock_delete, mock_print):
        """Test deleting space when operation fails."""
        mock_config.return_value.current_space = "default"
        mock_delete.return_value = False
        
        handle_space_command("delete old-space")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Failed to delete space" in output

    @patch('builtins.print')
    def test_handle_space_command_invalid(self, mock_print):
        """Test invalid space command."""
        handle_space_command("invalid")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Unknown space command" in output


class TestLegacyExportHandlers:
    """Test legacy export command handlers."""

    def setup_method(self):
        reset_context()

    @patch('builtins.print')
    def test_handle_export_command_no_history(self, mock_print):
        """Test export when no conversation history."""
        ctx = get_context()
        ctx.conversation_history = []
        
        handle_export_command("json")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "No conversation history to export" in output

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open')
    @patch('datetime.datetime')
    @patch('json.dump')
    def test_handle_export_command_json(self, mock_json_dump, mock_datetime, mock_open, mock_makedirs, mock_print):
        """Test JSON export."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Test message")]
        
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        # Mock the file object
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        handle_export_command("json")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Exported conversation to:" in output
        assert "Format: json" in output
        assert "conversation_20240101_120000.json" in output

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=lambda: MagicMock())
    @patch('datetime.datetime')
    def test_handle_export_command_txt(self, mock_datetime, mock_open, mock_makedirs, mock_print):
        """Test TXT export."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Test message")]
        
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        
        handle_export_command("txt")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Exported conversation to:" in output
        assert "Format: txt" in output

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=lambda: MagicMock())
    @patch('datetime.datetime')
    def test_handle_export_command_md(self, mock_datetime, mock_open, mock_makedirs, mock_print):
        """Test Markdown export."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Test message")]
        
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        
        handle_export_command("md")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Exported conversation to:" in output
        assert "Format: md" in output

    @patch('builtins.print')
    def test_handle_export_command_invalid_format(self, mock_print):
        """Test export with invalid format."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Test message")]
        
        handle_export_command("invalid")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Invalid format: invalid" in output

    @patch('builtins.print')
    @patch('os.makedirs')
    @patch('builtins.open')
    @patch('datetime.datetime')
    @patch('json.dump')
    def test_handle_export_command_json_error(self, mock_json_dump, mock_datetime, mock_open, mock_makedirs, mock_print):
        """Test JSON export with error."""
        ctx = get_context()
        ctx.conversation_history = [HumanMessage(content="Test message")]
        
        mock_datetime.now.return_value.strftime.return_value = "20240101_120000"
        mock_datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
        
        # Mock the file object
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock json.dump to raise an error
        mock_json_dump.side_effect = Exception("JSON error")
        
        handle_export_command("json")
        
        output = "\n".join(" ".join(map(str, call[0])) for call in mock_print.call_args_list)
        assert "Error exporting conversation" in output
        assert "JSON error" in output