#!/usr/bin/env python3
"""
Test suite for System Command Handlers (src/commands/handlers/system_commands.py).

Tests cover:
- /search command
- /shell command
- Argument parsing
- Error handling
"""

import pytest
from unittest.mock import patch, MagicMock

from src.commands.handlers.system_commands import handle_search, handle_shell


class TestSearchCommand:
    """Test /search command handler."""

    @patch("builtins.print")
    def test_search_no_args_shows_usage(self, mock_print):
        """Test that /search without args shows usage."""
        handle_search([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Usage" in output
        assert "--type" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_basic(self, mock_execute, mock_print):
        """Test basic search."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 2,
            "total_found": 2,
            "truncated": False,
            "matches": [
                {"file": "src/main.py", "line": 10, "content": "def main():"},
                {"file": "src/app.py", "line": 20, "content": "def main_loop():"},
            ],
        }

        handle_search(["def main"])

        mock_execute.assert_called_with(
            pattern="def main",
            path=".",
            file_type=None,
            max_results=50,
            case_sensitive=False,
        )
        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "src/main.py" in output
        assert "def main():" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_with_type(self, mock_execute, mock_print):
        """Test search with file type filter."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 0,
            "total_found": 0,
            "truncated": False,
            "matches": [],
        }

        handle_search(["TODO", "--type", "py"])

        mock_execute.assert_called_with(
            pattern="TODO",
            path=".",
            file_type="py",
            max_results=50,
            case_sensitive=False,
        )

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_with_path(self, mock_execute, mock_print):
        """Test search with custom path."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 0,
            "total_found": 0,
            "truncated": False,
            "matches": [],
        }

        handle_search(["pattern", "--path", "src/"])

        mock_execute.assert_called_with(
            pattern="pattern",
            path="src/",
            file_type=None,
            max_results=50,
            case_sensitive=False,
        )

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_with_limit(self, mock_execute, mock_print):
        """Test search with custom limit."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 0,
            "total_found": 0,
            "truncated": False,
            "matches": [],
        }

        handle_search(["pattern", "--limit", "20"])

        mock_execute.assert_called_with(
            pattern="pattern",
            path=".",
            file_type=None,
            max_results=20,
            case_sensitive=False,
        )

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_case_sensitive(self, mock_execute, mock_print):
        """Test case-sensitive search."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 0,
            "total_found": 0,
            "truncated": False,
            "matches": [],
        }

        handle_search(["Pattern", "-s"])

        mock_execute.assert_called_with(
            pattern="Pattern",
            path=".",
            file_type=None,
            max_results=50,
            case_sensitive=True,
        )

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_no_matches(self, mock_execute, mock_print):
        """Test search with no matches."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 0,
            "total_found": 0,
            "truncated": False,
            "matches": [],
        }

        handle_search(["nonexistent_pattern_xyz"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "No matches found" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_truncated_results(self, mock_execute, mock_print):
        """Test search with truncated results."""
        mock_execute.return_value = {
            "success": True,
            "match_count": 50,
            "total_found": 100,
            "truncated": True,
            "matches": [{"file": f"file{i}.py", "line": i, "content": "match"} for i in range(50)],
        }

        handle_search(["pattern"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "truncated" in output.lower()

    @patch("builtins.print")
    @patch("src.commands.handlers.system_commands.execute_code_search")
    def test_search_error(self, mock_execute, mock_print):
        """Test search error handling."""
        mock_execute.return_value = {"error": "ripgrep not installed"}

        handle_search(["pattern"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "ripgrep" in output

    @patch("builtins.print")
    def test_search_invalid_limit(self, mock_print):
        """Test search with invalid limit value."""
        handle_search(["pattern", "--limit", "abc"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Invalid limit" in output


class TestShellCommand:
    """Test /shell command handler."""

    @patch("builtins.print")
    def test_shell_no_args_shows_usage(self, mock_print):
        """Test that /shell without args shows usage."""
        handle_shell([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Usage" in output
        assert "Examples" in output

    @patch("os.getenv")
    @patch("builtins.print")
    @patch("src.tools.executors.shell_tools.execute_shell")
    def test_shell_success(self, mock_execute, mock_print, mock_getenv):
        """Test successful shell command."""
        mock_getenv.return_value = "cli"
        mock_execute.return_value = {
            "success": True,
            "return_code": 0,
            "stdout": "Hello World",
            "stderr": "",
        }

        handle_shell(["echo", "Hello", "World"])

        mock_execute.assert_called_with("echo Hello World")
        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Hello World" in output
        assert "successfully" in output.lower()

    @patch("os.getenv")
    @patch("builtins.print")
    @patch("src.tools.executors.shell_tools.execute_shell")
    def test_shell_command_failure(self, mock_execute, mock_print, mock_getenv):
        """Test shell command failure."""
        mock_getenv.return_value = "cli"
        mock_execute.return_value = {
            "success": False,
            "return_code": 1,
            "stdout": "",
            "stderr": "Error occurred",
        }

        handle_shell(["false"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "failed" in output.lower() or "exit code" in output.lower()

    @patch("os.getenv")
    @patch("builtins.print")
    @patch("src.tools.executors.shell_tools.execute_shell")
    def test_shell_blocked_command(self, mock_execute, mock_print, mock_getenv):
        """Test blocked shell command."""
        mock_getenv.return_value = "cli"
        mock_execute.return_value = {"error": "Command 'rm' is blocked"}

        handle_shell(["rm", "-rf", "/"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "blocked" in output.lower()

    @patch("os.getenv")
    @patch("builtins.print")
    def test_shell_blocked_in_gui_mode(self, mock_print, mock_getenv):
        """Test that shell is blocked in GUI mode."""
        mock_getenv.return_value = "gui"

        handle_shell(["ls"])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "disabled" in output.lower() or "GUI" in output


class TestSystemCommandAliases:
    """Test command aliases."""

    def test_search_registered_with_aliases(self):
        """Test that search has grep, rg, and find-code aliases."""
        # Force reload to re-register after any registry.clear() calls
        import importlib
        from src.commands.handlers import system_commands
        importlib.reload(system_commands)
        from src.commands.registry import CommandRegistry

        assert CommandRegistry.has_command("search")
        assert CommandRegistry.has_command("grep")
        assert CommandRegistry.has_command("rg")
        assert CommandRegistry.has_command("find-code")

    def test_shell_registered_with_aliases(self):
        """Test that shell has sh, exec, and run aliases."""
        # Force reload to re-register after any registry.clear() calls
        import importlib
        from src.commands.handlers import system_commands
        importlib.reload(system_commands)
        from src.commands.registry import CommandRegistry

        assert CommandRegistry.has_command("shell")
        assert CommandRegistry.has_command("sh")
        assert CommandRegistry.has_command("exec")
        assert CommandRegistry.has_command("run")
