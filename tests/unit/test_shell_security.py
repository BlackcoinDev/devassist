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
Shell Security Tests

Tests for shell command security validation:
- Safe command detection
- Blocked command detection
- Dangerous pattern detection
- Command parsing
"""

import pytest
from src.security.shell_security import ShellSecurity
from src.security.exceptions import SecurityError


class TestShellSecurityValidation:
    """Test shell command validation."""

    def test_safe_command_git(self):
        """Test that git commands are considered safe."""
        status, reason, requires_approval = ShellSecurity.validate_command("git status")

        assert status == "safe"
        assert not requires_approval

    def test_safe_command_python(self):
        """Test that python commands are considered safe."""
        status, reason, requires_approval = ShellSecurity.validate_command("python --version")

        assert status == "safe"
        assert not requires_approval

    def test_safe_command_ls(self):
        """Test that ls commands are considered safe."""
        status, reason, requires_approval = ShellSecurity.validate_command("ls -la")

        assert status == "safe"

    def test_blocked_command_rm(self):
        """Test that rm command is blocked."""
        status, reason, requires_approval = ShellSecurity.validate_command("rm -rf /")

        assert status == "blocked"
        assert "blocked" in reason.lower()
        assert not requires_approval

    def test_blocked_command_sudo(self):
        """Test that sudo command is blocked."""
        status, reason, requires_approval = ShellSecurity.validate_command("sudo apt update")

        assert status == "blocked"
        assert not requires_approval

    def test_blocked_command_chmod(self):
        """Test that chmod command is blocked."""
        status, reason, requires_approval = ShellSecurity.validate_command("chmod 777 file.txt")

        assert status == "blocked"

    def test_unknown_command_requires_approval(self):
        """Test that unknown commands require approval."""
        status, reason, requires_approval = ShellSecurity.validate_command("custom_script.sh")

        assert status == "unknown"
        assert requires_approval

    def test_dangerous_pattern_command_chaining(self):
        """Test detection of command chaining with &&."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("ls && rm -rf /")

        assert "Dangerous" in str(exc_info.value)

    def test_dangerous_pattern_semicolon(self):
        """Test detection of command separator with ;."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("ls; rm -rf /")

        assert "Dangerous" in str(exc_info.value)

    def test_dangerous_pattern_pipe(self):
        """Test detection of pipe operator."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("cat file.txt | grep password")

        assert "Dangerous" in str(exc_info.value)

    def test_dangerous_pattern_redirect(self):
        """Test detection of output redirection."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("echo password > file.txt")

        assert "Dangerous" in str(exc_info.value)

    def test_dangerous_pattern_command_substitution(self):
        """Test detection of command substitution with $(...)."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("echo $(whoami)")

        assert "Dangerous" in str(exc_info.value)

    def test_dangerous_pattern_backtick(self):
        """Test detection of command substitution with backticks."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("echo `whoami`")

        assert "Dangerous" in str(exc_info.value)

    def test_empty_command(self):
        """Test empty command validation."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("")

        assert "Empty command" in str(exc_info.value)

    def test_whitespace_only_command(self):
        """Test whitespace-only command validation."""
        with pytest.raises(SecurityError) as exc_info:
            ShellSecurity.validate_command("   ")

        assert "Empty command" in str(exc_info.value)


class TestShellSecurityHelpers:
    """Test helper methods."""

    def test_is_safe_returns_true_for_safe_commands(self):
        """Test is_safe returns True for safe commands."""
        assert ShellSecurity.is_safe("git status") is True
        assert ShellSecurity.is_safe("python script.py") is True
        assert ShellSecurity.is_safe("ls -la") is True

    def test_is_safe_returns_false_for_blocked_commands(self):
        """Test is_safe returns False for blocked commands."""
        assert ShellSecurity.is_safe("rm -rf /") is False
        assert ShellSecurity.is_safe("sudo apt update") is False

    def test_is_safe_returns_false_for_dangerous_patterns(self):
        """Test is_safe returns False for dangerous patterns."""
        assert ShellSecurity.is_safe("ls && rm file") is False
        assert ShellSecurity.is_safe("echo test | cat") is False

    def test_is_blocked_returns_true_for_blocked_commands(self):
        """Test is_blocked returns True for blocked commands."""
        assert ShellSecurity.is_blocked("rm -rf /") is True
        assert ShellSecurity.is_blocked("sudo command") is True

    def test_is_blocked_returns_true_for_dangerous_patterns(self):
        """Test is_blocked returns True for dangerous patterns."""
        assert ShellSecurity.is_blocked("ls && rm file") is True

    def test_is_blocked_returns_false_for_safe_commands(self):
        """Test is_blocked returns False for safe commands."""
        assert ShellSecurity.is_blocked("git status") is False

    def test_get_base_command_simple(self):
        """Test extracting base command from simple command."""
        assert ShellSecurity.get_base_command("git status") == "git"
        assert ShellSecurity.get_base_command("python script.py") == "python"

    def test_get_base_command_with_flags(self):
        """Test extracting base command with flags."""
        assert ShellSecurity.get_base_command("ls -la --all") == "ls"

    def test_get_base_command_with_quotes(self):
        """Test extracting base command with quoted arguments."""
        assert ShellSecurity.get_base_command('echo "hello world"') == "echo"

    def test_get_base_command_empty(self):
        """Test get_base_command with empty string."""
        with pytest.raises(SecurityError):
            ShellSecurity.get_base_command("")

    def test_get_base_command_invalid_syntax(self):
        """Test get_base_command with invalid shell syntax."""
        with pytest.raises(SecurityError):
            ShellSecurity.get_base_command('echo "unclosed quote')


class TestShellSecurityEdgeCases:
    """Test edge cases and special scenarios."""

    def test_npm_commands_safe(self):
        """Test that npm commands are safe."""
        assert ShellSecurity.is_safe("npm install") is True
        assert ShellSecurity.is_safe("npm run build") is True
        assert ShellSecurity.is_safe("npx create-react-app myapp") is True

    def test_pytest_commands_safe(self):
        """Test that pytest commands are safe."""
        assert ShellSecurity.is_safe("pytest tests/") is True
        assert ShellSecurity.is_safe("pytest -v --cov") is True

    def test_docker_commands_safe(self):
        """Test that docker commands are safe."""
        assert ShellSecurity.is_safe("docker ps") is True
        assert ShellSecurity.is_safe("docker images") is True

    def test_curl_commands_safe(self):
        """Test that curl commands are safe."""
        assert ShellSecurity.is_safe("curl https://example.com") is True

    def test_kill_command_blocked(self):
        """Test that kill commands are blocked."""
        assert ShellSecurity.is_blocked("kill -9 1234") is True
        assert ShellSecurity.is_blocked("killall python") is True

    def test_apt_command_blocked(self):
        """Test that apt commands are blocked."""
        assert ShellSecurity.is_blocked("apt install package") is True
        assert ShellSecurity.is_blocked("apt-get update") is True

    def test_command_with_path(self):
        """Test command with absolute path."""
        status, _, _ = ShellSecurity.validate_command("/usr/bin/python script.py")
        # Unknown because /usr/bin/python is not in safe list
        assert status == "unknown"

    def test_safe_commands_set_contains_expected(self):
        """Test that SAFE_COMMANDS contains expected entries."""
        expected = {"git", "npm", "python", "pytest", "ls", "cat", "grep"}
        for cmd in expected:
            assert cmd in ShellSecurity.SAFE_COMMANDS

    def test_blocked_commands_set_contains_expected(self):
        """Test that BLOCKED_COMMANDS contains expected entries."""
        expected = {"rm", "sudo", "chmod", "chown", "kill", "killall"}
        for cmd in expected:
            assert cmd in ShellSecurity.BLOCKED_COMMANDS
