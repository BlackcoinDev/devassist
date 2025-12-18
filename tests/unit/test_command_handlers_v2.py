#!/usr/bin/env python3
"""
Unit tests for command handlers, targeting coverage gaps in Phase 6.
Focus: Legacy commands, Learning commands, Memory commands.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.commands.handlers.learning_commands import handle_learn, handle_web, handle_populate
from src.commands.handlers.memory_commands import handle_memory, handle_clear, handle_mem0
from src.commands.handlers.legacy_commands import handle_read_command, handle_write_command
from src.commands.handlers.config_commands import handle_context, handle_learning
from src.core.context import ApplicationContext, get_context, set_context

class TestLegacyCommands:
    """Test legacy command handlers."""

    def setup_method(self):
        set_context(ApplicationContext())

    @patch('src.commands.handlers.legacy_commands.execute_read_file')
    @patch('builtins.print')
    def test_read_command_success(self, mock_print, mock_exec):
        """Test /read command success path."""
        mock_exec.return_value = {
            "content": "line1\nline2",
            "file_info": {"name": "test.txt", "size": 10, "lines": 2}
        }
        handle_read_command("test.txt")
        mock_exec.assert_called_with("test.txt")
        # Verify output
        assert any("line1" in str(call) for call in mock_print.call_args_list)

    @patch('src.commands.handlers.legacy_commands.execute_read_file')
    @patch('builtins.print')
    def test_read_command_error(self, mock_print, mock_exec):
        """Test /read command error path."""
        mock_exec.return_value = {"error": "File not found"}
        handle_read_command("bad.txt")
        mock_print.assert_any_call("\n❌ Error reading file: File not found\n")

    @patch('builtins.print')
    def test_read_command_no_args(self, mock_print):
        """Test /read command without arguments."""
        handle_read_command("")
        mock_print.assert_any_call("\n❌ Please specify a file path. Example: /read README.md\n")

    @patch('src.commands.handlers.legacy_commands.execute_write_file')
    @patch('builtins.print')
    def test_write_command_success(self, mock_print, mock_exec):
        """Test /write command success path."""
        mock_exec.return_value = {"success": True, "bytes_written": 5}
        handle_write_command("test.txt:content")
        mock_exec.assert_called_with("test.txt", "content")
        mock_print.assert_any_call("\n✅ File 'test.txt' written successfully")
        mock_print.assert_any_call(f"📄 Wrote {len('content')} characters\n")

    @patch('builtins.print')
    def test_write_command_invalid_format(self, mock_print):
        """Test /write command with invalid format."""
        handle_write_command("invalid_args")
        # Check that usage help is printed
        assert any("Usage: /write" in str(call) for call in mock_print.call_args_list)


class TestLearningCommands:
    """Test learning command handlers."""

    def setup_method(self):
        ctx = ApplicationContext()
        ctx.vectorstore = Mock() # mock vectorstore to simulate availability
        set_context(ctx)

    @patch('src.commands.handlers.learning_commands.add_to_knowledge_base')
    @patch('builtins.print')
    def test_learn_command_success(self, mock_print, mock_add):
        """Test /learn command success."""
        mock_add.return_value = True
        handle_learn(["python", "is", "great"])
        mock_add.assert_called_with("python is great")
        assert any("✅ Learned:" in str(call) for call in mock_print.call_args_list)

    @patch('builtins.print')
    def test_learn_command_no_vectorstore(self, mock_print):
        """Test /learn command when vectorstore unavailable."""
        get_context().vectorstore = None
        handle_learn(["data"])
        mock_print.assert_any_call("\nVector database not available. ChromaDB is required for learning features.\n")

    @patch('builtins.print')
    def test_learn_command_empty(self, mock_print):
        """Test /learn command with no args."""
        handle_learn([])
        mock_print.assert_any_call("\nUsage: /learn <information to remember>\n")

    @patch('src.main.execute_learn_url')
    @patch('builtins.print')
    def test_web_command_success(self, mock_print, mock_exec):
        """Test /web command success."""
        mock_exec.return_value = {"success": True}
        handle_web(["http://example.com"])
        mock_exec.assert_called_with("http://example.com")
        assert any("Successfully learned" in str(call) for call in mock_print.call_args_list)

    @patch('src.main.execute_learn_url')
    @patch('builtins.print')
    def test_web_command_error(self, mock_print, mock_exec):
        """Test /web command error."""
        mock_exec.return_value = {"error": "404 Not Found"}
        handle_web(["http://bad.com"])
        mock_print.assert_any_call("\n❌ Error: 404 Not Found\n")

    @patch('src.commands.handlers.learning_commands.add_to_knowledge_base')
    @patch('builtins.print')
    def test_learn_command_failure(self, mock_print, mock_add):
        """Test /learn command when adding to knowledge base fails."""
        mock_add.return_value = False
        handle_learn(["test", "information"])
        mock_print.assert_any_call("\n❌ Failed to learn information\n")

    @patch('src.main.handle_populate_command')
    @patch('builtins.print')
    def test_populate_command_with_path(self, mock_print, mock_populate):
        """Test /populate command with directory path."""
        handle_populate(["src/", "tests/"])
        mock_populate.assert_called_with("src/ tests/")

    @patch('src.main.handle_populate_command')
    @patch('builtins.print')
    def test_populate_command_empty(self, mock_print, mock_populate):
        """Test /populate command without arguments."""
        handle_populate([])
        mock_populate.assert_called_with("")

    @patch('builtins.print')
    def test_web_command_no_url(self, mock_print):
        """Test /web command without URL argument."""
        handle_web([])
        mock_print.assert_any_call("\nUsage: /web <url>\n")


class TestMemoryCommands:
    """Test memory command handlers."""

    def setup_method(self):
        set_context(ApplicationContext())

    @patch('builtins.print')
    def test_memory_command_empty(self, mock_print):
        """Test /memory command with empty history."""
        handle_memory([])
        mock_print.assert_any_call("\n📝 No conversation history available.\n")

    @patch('builtins.print')
    def test_memory_command_with_history(self, mock_print):
        """Test /memory command with history."""
        ctx = get_context()
        ctx.conversation_history = [Mock(content="Hi"), Mock(content="Hello")]
        handle_memory([])
        # Verify header and content printed
        assert any("Conversation History" in str(call) for call in mock_print.call_args_list)

    @patch('builtins.input', side_effect=["y"])
    @patch('src.commands.handlers.memory_commands.save_memory')
    @patch('builtins.print')
    def test_clear_command_confirmed(self, mock_print, mock_save, mock_input):
        """Test /clear command with confirmation."""
        handle_clear([])
        mock_save.assert_called()
        assert len(get_context().conversation_history) == 1 # 1 system message
        mock_print.assert_any_call("\nConversation memory cleared. Starting fresh.\n")

    @patch('builtins.input', side_effect=["n"])
    @patch('builtins.print')
    def test_clear_command_cancelled(self, mock_print, mock_input):
        """Test /clear command cancelled."""
        ctx = get_context()
        ctx.conversation_history = [Mock()] # Has history
        handle_clear([])
        assert len(get_context().conversation_history) == 1
        mock_print.assert_any_call("\n❌ Clear cancelled\n")

    @patch('builtins.print')
    def test_mem0_command_unavailable(self, mock_print):
        """Test /mem0 command when unavailable."""
        get_context().user_memory = None
        handle_mem0([])
        mock_print.assert_any_call("\n❌ Mem0 not available.\n")

    @patch('builtins.print')
    def test_mem0_command_success(self, mock_print):
        """Test /mem0 command success."""
        ctx = get_context()
        ctx.user_memory = Mock()
        ctx.user_memory.get_all.return_value = {"results": [{"memory": "User likes python"}]}

        handle_mem0([])

        assert any("User likes python" in str(call) for call in mock_print.call_args_list)

    @patch('builtins.print')
    def test_mem0_command_empty_memories(self, mock_print):
        """Test /mem0 command with no memories."""
        ctx = get_context()
        ctx.user_memory = Mock()
        ctx.user_memory.get_all.return_value = {"results": []}

        handle_mem0([])

        mock_print.assert_any_call("📊 No personalized memories stored yet.")

    @patch('builtins.print')
    def test_mem0_command_long_content_truncation(self, mock_print):
        """Test /mem0 command with long memory content that gets truncated."""
        ctx = get_context()
        ctx.user_memory = Mock()
        long_content = "A" * 250  # 250 characters, should be truncated
        ctx.user_memory.get_all.return_value = {"results": [{"memory": long_content}]}

        handle_mem0([])

        # Verify truncation occurred
        calls_str = str(mock_print.call_args_list)
        assert "..." in calls_str

    @patch('builtins.print')
    def test_mem0_command_many_memories(self, mock_print):
        """Test /mem0 command with more than 5 memories."""
        ctx = get_context()
        ctx.user_memory = Mock()
        # Create 10 memories
        memories = [{"memory": f"Memory {i}"} for i in range(10)]
        ctx.user_memory.get_all.return_value = {"results": memories}

        handle_mem0([])

        # Should show "... and 5 more"
        assert any("and 5 more" in str(call) for call in mock_print.call_args_list)

    @patch('builtins.print')
    def test_mem0_command_exception(self, mock_print):
        """Test /mem0 command with exception during retrieval."""
        ctx = get_context()
        ctx.user_memory = Mock()
        ctx.user_memory.get_all.side_effect = Exception("Connection error")

        handle_mem0([])

        # Should show error message
        assert any("Failed to retrieve Mem0 contents" in str(call) for call in mock_print.call_args_list)


class TestConfigCommands:
    """Test configuration command handlers."""

    def setup_method(self):
        set_context(ApplicationContext())

    @patch('src.commands.handlers.config_commands.set_learning_mode')
    @patch('builtins.print')
    def test_learning_command_set_normal(self, mock_print, mock_set_mode):
        """Test /learning command with normal mode."""
        handle_learning(["normal"])
        mock_set_mode.assert_called_with("normal")
        mock_print.assert_any_call("\n✅ Learning mode set to: normal\n")

    @patch('src.commands.handlers.config_commands.set_learning_mode')
    @patch('builtins.print')
    def test_learning_command_set_strict(self, mock_print, mock_set_mode):
        """Test /learning command with strict mode."""
        handle_learning(["strict"])
        mock_set_mode.assert_called_with("strict")
        mock_print.assert_any_call("\n✅ Learning mode set to: strict\n")

    @patch('src.commands.handlers.config_commands.set_learning_mode')
    @patch('builtins.print')
    def test_learning_command_set_off(self, mock_print, mock_set_mode):
        """Test /learning command with off mode."""
        handle_learning(["off"])
        mock_set_mode.assert_called_with("off")
        mock_print.assert_any_call("\n✅ Learning mode set to: off\n")

    @patch('builtins.print')
    def test_learning_command_invalid_mode(self, mock_print):
        """Test /learning command with invalid mode."""
        handle_learning(["invalid"])
        mock_print.assert_any_call("\n❌ Invalid learning mode: invalid")
        mock_print.assert_any_call("Valid options: normal, strict, off\n")

    @patch('src.commands.handlers.config_commands.set_context_mode')
    @patch('builtins.print')
    def test_context_command_set_auto(self, mock_print, mock_set_mode):
        """Test /context command with auto mode."""
        handle_context(["auto"])
        mock_set_mode.assert_called_with("auto")
        mock_print.assert_any_call("\n✅ Context mode set to: auto\n")

    @patch('src.commands.handlers.config_commands.set_context_mode')
    @patch('builtins.print')
    def test_context_command_set_on(self, mock_print, mock_set_mode):
        """Test /context command with on mode."""
        handle_context(["on"])
        mock_set_mode.assert_called_with("on")
        mock_print.assert_any_call("\n✅ Context mode set to: on\n")

    @patch('src.commands.handlers.config_commands.set_context_mode')
    @patch('builtins.print')
    def test_context_command_set_off(self, mock_print, mock_set_mode):
        """Test /context command with off mode."""
        handle_context(["off"])
        mock_set_mode.assert_called_with("off")
        mock_print.assert_any_call("\n✅ Context mode set to: off\n")

    @patch('builtins.print')
    def test_context_command_invalid_mode(self, mock_print):
        """Test /context command with invalid mode."""
        handle_context(["invalid"])
        mock_print.assert_any_call("\n❌ Invalid context mode: invalid")
        mock_print.assert_any_call("Valid options: auto, on, off\n")
