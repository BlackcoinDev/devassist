#!/usr/bin/env python3
"""
Test suite for Git Command Handlers (src/commands/handlers/git_commands.py).

Tests cover:
- /git-status command
- /git-log command
- /git-diff command
- Aliases (gs, gl, gd)
"""

from unittest.mock import patch, MagicMock

from src.commands.handlers.git_commands import (
    handle_git_status,
    handle_git_log,
    handle_git_diff,
)


class TestGitStatusCommand:
    """Test /git-status command handler."""

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_status")
    def test_git_status_clean_repo(self, mock_execute, mock_print):
        """Test status display for clean repository."""
        mock_execute.return_value = {
            "success": True,
            "branch": "main",
            "is_clean": True,
            "staged": [],
            "unstaged": [],
            "untracked": [],
        }

        handle_git_status([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "main" in output
        assert "clean" in output.lower()

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_status")
    def test_git_status_with_changes(self, mock_execute, mock_print):
        """Test status display with changes."""
        mock_execute.return_value = {
            "success": True,
            "branch": "develop",
            "is_clean": False,
            "staged": ["M file1.py"],
            "unstaged": ["M file2.py"],
            "untracked": ["new.txt"],
        }

        handle_git_status([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "develop" in output
        assert "Staged" in output
        assert "file1.py" in output
        assert "Unstaged" in output
        assert "Untracked" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_status")
    def test_git_status_error(self, mock_execute, mock_print):
        """Test error handling."""
        mock_execute.return_value = {"error": "Not a git repository"}

        handle_git_status([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Not a git repository" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_status")
    def test_git_status_truncates_long_lists(self, mock_execute, mock_print):
        """Test that long file lists are truncated."""
        mock_execute.return_value = {
            "success": True,
            "branch": "main",
            "is_clean": False,
            "staged": [f"M file{i}.py" for i in range(20)],
            "unstaged": [],
            "untracked": [],
        }

        handle_git_status([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "and 10 more" in output


class TestGitLogCommand:
    """Test /git-log command handler."""

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_log")
    def test_git_log_basic(self, mock_execute, mock_print):
        """Test basic log display."""
        mock_execute.return_value = {
            "success": True,
            "commit_count": 2,
            "commits": [
                {"hash": "abc1234", "author": "John", "date": "2024-01-15", "message": "First commit"},
                {"hash": "def5678", "author": "Jane", "date": "2024-01-16", "message": "Second commit"},
            ],
        }

        handle_git_log([])

        mock_execute.assert_called_with(limit=10, file_path=None)
        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "abc1234" in output
        assert "John" in output
        assert "First commit" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_log")
    def test_git_log_with_limit(self, mock_execute, mock_print):
        """Test log with custom limit."""
        mock_execute.return_value = {
            "success": True,
            "commit_count": 0,
            "commits": [],
        }

        handle_git_log(["5"])

        mock_execute.assert_called_with(limit=5, file_path=None)

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_log")
    def test_git_log_with_file_path(self, mock_execute, mock_print):
        """Test log for specific file."""
        mock_execute.return_value = {
            "success": True,
            "commit_count": 0,
            "commits": [],
        }

        handle_git_log(["src/main.py"])

        mock_execute.assert_called_with(limit=10, file_path="src/main.py")

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_log")
    def test_git_log_with_limit_and_file(self, mock_execute, mock_print):
        """Test log with limit and file path."""
        mock_execute.return_value = {
            "success": True,
            "commit_count": 0,
            "commits": [],
        }

        handle_git_log(["20", "src/main.py"])

        mock_execute.assert_called_with(limit=20, file_path="src/main.py")

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_log")
    def test_git_log_error(self, mock_execute, mock_print):
        """Test error handling."""
        mock_execute.return_value = {"error": "Not a git repository"}

        handle_git_log([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Not a git repository" in output


class TestGitDiffCommand:
    """Test /git-diff command handler."""

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_diff")
    def test_git_diff_basic(self, mock_execute, mock_print):
        """Test basic diff display."""
        mock_execute.return_value = {
            "success": True,
            "has_changes": True,
            "diff": "+new line\n-old line",
            "staged": False,
        }

        handle_git_diff([])

        mock_execute.assert_called_with(file_path=None, staged=False)
        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Unstaged" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_diff")
    def test_git_diff_staged(self, mock_execute, mock_print):
        """Test staged diff."""
        mock_execute.return_value = {
            "success": True,
            "has_changes": True,
            "diff": "diff content",
            "staged": True,
        }

        handle_git_diff(["--staged"])

        mock_execute.assert_called_with(file_path=None, staged=True)
        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Staged" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_diff")
    def test_git_diff_specific_file(self, mock_execute, mock_print):
        """Test diff for specific file."""
        mock_execute.return_value = {
            "success": True,
            "has_changes": False,
            "message": "No unstaged changes",
        }

        handle_git_diff(["src/main.py"])

        mock_execute.assert_called_with(file_path="src/main.py", staged=False)

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_diff")
    def test_git_diff_staged_and_file(self, mock_execute, mock_print):
        """Test staged diff for specific file."""
        mock_execute.return_value = {
            "success": True,
            "has_changes": False,
            "message": "No staged changes",
        }

        handle_git_diff(["--staged", "src/main.py"])

        mock_execute.assert_called_with(file_path="src/main.py", staged=True)

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_diff")
    def test_git_diff_no_changes(self, mock_execute, mock_print):
        """Test display when no changes."""
        mock_execute.return_value = {
            "success": True,
            "has_changes": False,
            "message": "No unstaged changes",
        }

        handle_git_diff([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "No" in output

    @patch("builtins.print")
    @patch("src.commands.handlers.git_commands.execute_git_diff")
    def test_git_diff_error(self, mock_execute, mock_print):
        """Test error handling."""
        mock_execute.return_value = {"error": "Not a git repository"}

        handle_git_diff([])

        output = "\n".join(
            " ".join(str(arg) for arg in call[0])
            for call in mock_print.call_args_list
        )
        assert "Not a git repository" in output


class TestGitCommandAliases:
    """Test command aliases."""

    def test_git_status_registered_with_aliases(self):
        """Test that git-status has gs and status aliases."""
        # Force reload to re-register after any registry.clear() calls
        import importlib
        from src.commands.handlers import git_commands
        importlib.reload(git_commands)
        from src.commands.registry import CommandRegistry

        assert CommandRegistry.has_command("git-status")
        assert CommandRegistry.has_command("gs")
        assert CommandRegistry.has_command("status")

    def test_git_log_registered_with_aliases(self):
        """Test that git-log has gl and log aliases."""
        # Force reload to re-register after any registry.clear() calls
        import importlib
        from src.commands.handlers import git_commands
        importlib.reload(git_commands)
        from src.commands.registry import CommandRegistry

        assert CommandRegistry.has_command("git-log")
        assert CommandRegistry.has_command("gl")
        assert CommandRegistry.has_command("log")

    def test_git_diff_registered_with_aliases(self):
        """Test that git-diff has gd and diff aliases."""
        # Force reload to re-register after any registry.clear() calls
        import importlib
        from src.commands.handlers import git_commands
        importlib.reload(git_commands)
        from src.commands.registry import CommandRegistry

        assert CommandRegistry.has_command("git-diff")
        assert CommandRegistry.has_command("gd")
        assert CommandRegistry.has_command("diff")
