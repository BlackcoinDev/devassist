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
Shell Tools Tests

Tests for shell_execute tool:
- Successful command execution
- GUI mode blocking
- Security validation
- Timeout handling
- Output truncation
"""

from unittest.mock import patch, MagicMock
import subprocess

from src.tools.executors.shell_tools import execute_shell

# Common mock path for the new working directory validation
MOCK_VALIDATE_CWD = "src.tools.executors.shell_tools._validate_working_directory"


class TestShellExecuteBasic:
    """Test basic shell execution functionality."""

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_success(self, mock_run, mock_getenv, mock_validate_cwd):
        """Test successful command execution."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Hello World\n", stderr=""
        )

        result = execute_shell("echo 'Hello World'")

        assert result["success"] is True
        assert result["return_code"] == 0
        assert "Hello World" in result["stdout"]
        assert result["stderr"] == ""

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_with_error_output(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test command execution with stderr output."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="Error: file not found\n"
        )

        result = execute_shell("cat nonexistent.txt")

        assert result["success"] is False
        assert result["return_code"] == 1
        assert "Error" in result["stderr"]

    @patch("os.getenv")
    def test_execute_shell_empty_command(self, mock_getenv):
        """Test execution with empty command."""
        mock_getenv.return_value = "cli"

        result = execute_shell("")

        assert "error" in result
        assert "Empty command" in result["error"]

    @patch("os.getenv")
    def test_execute_shell_whitespace_command(self, mock_getenv):
        """Test execution with whitespace-only command."""
        mock_getenv.return_value = "cli"

        result = execute_shell("   ")

        assert "error" in result
        assert "Empty command" in result["error"]


class TestShellExecuteGUIMode:
    """Test GUI mode restrictions."""

    @patch("os.getenv")
    def test_execute_shell_blocked_in_gui_mode(self, mock_getenv):
        """Test that shell execution is blocked in GUI mode."""
        mock_getenv.return_value = "gui"

        result = execute_shell("ls -la")

        assert "error" in result
        assert "disabled in GUI mode" in result["error"]

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_allowed_in_cli_mode(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that shell execution works in CLI mode."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = execute_shell("ls -la")

        assert "error" not in result
        assert result["success"] is True


class TestShellExecuteSecurity:
    """Test security validation."""

    @patch("os.getenv")
    def test_execute_shell_blocked_command_rm(self, mock_getenv):
        """Test that rm command is blocked."""
        mock_getenv.return_value = "cli"

        result = execute_shell("rm -rf /")

        assert "error" in result
        assert "blocked" in result["error"].lower()

    @patch("os.getenv")
    def test_execute_shell_blocked_command_sudo(self, mock_getenv):
        """Test that sudo command is blocked."""
        mock_getenv.return_value = "cli"

        result = execute_shell("sudo apt update")

        assert "error" in result
        assert "blocked" in result["error"].lower()

    @patch("os.getenv")
    def test_execute_shell_dangerous_pattern_pipe(self, mock_getenv):
        """Test that pipe operator is blocked."""
        mock_getenv.return_value = "cli"

        result = execute_shell("cat file.txt | grep password")

        assert "error" in result
        assert "Dangerous" in result["error"]

    @patch("os.getenv")
    def test_execute_shell_dangerous_pattern_chaining(self, mock_getenv):
        """Test that command chaining is blocked."""
        mock_getenv.return_value = "cli"

        result = execute_shell("ls && rm -rf /")

        assert "error" in result
        assert "Dangerous" in result["error"]

    @patch("os.getenv")
    def test_execute_shell_dangerous_pattern_redirect(self, mock_getenv):
        """Test that output redirection is blocked."""
        mock_getenv.return_value = "cli"

        result = execute_shell("echo password > secrets.txt")

        assert "error" in result
        assert "Dangerous" in result["error"]


class TestShellExecuteTimeout:
    """Test timeout handling."""

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_timeout(self, mock_run, mock_getenv, mock_validate_cwd):
        """Test command timeout handling."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.side_effect = subprocess.TimeoutExpired("sleep 100", 30)

        result = execute_shell("sleep 100", timeout=30)

        assert "error" in result
        assert "timed out" in result["error"].lower()

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_custom_timeout(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test custom timeout is passed to subprocess."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        execute_shell("long_command", timeout=120)

        # Check that subprocess.run was called with correct timeout
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 120

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_timeout_clamped_to_max(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that timeout is clamped to maximum (300s)."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        execute_shell("command", timeout=600)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 300

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_timeout_clamped_to_min(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that timeout is clamped to minimum (30s default)."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        execute_shell("command", timeout=0)

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 30


class TestShellExecuteOutputTruncation:
    """Test output truncation for large outputs."""

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_stdout_truncation(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that large stdout is truncated."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"

        large_output = "x" * (60 * 1024)  # 60KB output
        mock_run.return_value = MagicMock(returncode=0, stdout=large_output, stderr="")

        result = execute_shell("generate_output")

        assert result["stdout_truncated"] is True
        assert len(result["stdout"]) < len(large_output)
        assert "truncated" in result["stdout"]

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_stderr_truncation(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that large stderr is truncated."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"

        large_error = "e" * (60 * 1024)  # 60KB error output
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr=large_error)

        result = execute_shell("error_command")

        assert result["stderr_truncated"] is True
        assert len(result["stderr"]) < len(large_error)

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_no_truncation_for_small_output(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that small outputs are not truncated."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(
            returncode=0, stdout="small output", stderr=""
        )

        result = execute_shell("command")

        assert result["stdout_truncated"] is False
        assert result["stderr_truncated"] is False


class TestShellExecuteEdgeCases:
    """Test edge cases and error handling."""

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_general_exception(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test handling of general exceptions."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.side_effect = Exception("Unexpected error")

        result = execute_shell("command")

        assert "error" in result
        assert "Unexpected error" in result["error"]

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_returns_command_in_result(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that executed command is included in result."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/tmp"
        mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")

        result = execute_shell("git status")

        assert result["command"] == "git status"

    @patch(MOCK_VALIDATE_CWD)
    @patch("os.getenv")
    @patch("subprocess.run")
    def test_execute_shell_uses_validated_directory(
        self, mock_run, mock_getenv, mock_validate_cwd
    ):
        """Test that command runs in validated project directory."""
        mock_getenv.return_value = "cli"
        mock_validate_cwd.return_value = "/home/user/project"
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        execute_shell("ls")

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["cwd"] == "/home/user/project"
