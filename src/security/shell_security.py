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
Shell command security utilities for DevAssist.

Provides command validation using allowlist/blocklist approach to prevent
execution of dangerous shell commands.
"""

import shlex
from typing import Tuple

from src.security.exceptions import SecurityError


class ShellSecurity:
    """
    Shell command security validator using allowlist/blocklist approach.

    Features:
    - Safe commands run without confirmation
    - Dangerous commands are always blocked
    - Unknown commands require user confirmation (via approval system)

    All methods are class methods for stateless operation.
    """

    # Commands that are safe to execute without user confirmation
    SAFE_COMMANDS: set[str] = {
        # Version control
        "git",
        # Package managers
        "npm", "npx", "yarn", "pnpm", "pip", "uv",
        # Python
        "python", "python3", "pytest", "mypy", "flake8", "black", "ruff",
        # Read-only utilities
        "cat", "ls", "pwd", "echo", "head", "tail", "wc", "sort", "uniq",
        "grep", "rg", "find", "which", "whereis", "file", "stat", "date",
        "whoami", "hostname", "uname", "env", "printenv",
        # Development tools
        "node", "deno", "bun", "cargo", "go", "make", "cmake",
        # Text processing
        "awk", "sed", "cut", "tr", "diff", "less", "more",
        # Network (read-only)
        "curl", "wget", "ping", "dig", "nslookup", "host",
        # Archive (read-only)
        "tar", "zip", "unzip", "gzip", "gunzip",
        # Docker (read operations)
        "docker",
    }

    # Commands that are always blocked (dangerous operations)
    BLOCKED_COMMANDS: set[str] = {
        # Destructive file operations
        "rm", "rmdir", "shred",
        # Privilege escalation
        "sudo", "su", "doas", "pkexec",
        # Permission changes
        "chmod", "chown", "chgrp",
        # Disk operations
        "dd", "mkfs", "fdisk", "parted", "mount", "umount",
        # System modification
        "systemctl", "service", "init", "shutdown", "reboot", "halt",
        # User management
        "useradd", "userdel", "usermod", "passwd", "adduser", "deluser",
        # Network configuration
        "iptables", "ip6tables", "ufw", "firewall-cmd",
        # Package management (system-wide)
        "apt", "apt-get", "yum", "dnf", "pacman", "brew",
        # Shell manipulation
        "eval", "exec", "source",
        # Process control
        "kill", "killall", "pkill",
        # Dangerous utilities
        "nc", "netcat", "ncat",
    }

    # Dangerous shell operators and patterns
    DANGEROUS_PATTERNS: list[str] = [
        "&&",       # Command chaining
        "||",       # Conditional execution
        ";",        # Command separator
        "|",        # Pipe (can be dangerous)
        ">",        # Output redirection
        ">>",       # Append redirection
        "<",        # Input redirection
        "`",        # Command substitution
        "$(",       # Command substitution
        "${",       # Variable expansion
        "\\n",      # Newline injection
        "\n",       # Literal newline
    ]

    @classmethod
    def validate_command(cls, command: str) -> Tuple[str, str, bool]:
        """
        Validate a shell command for security.

        Args:
            command: The shell command to validate

        Returns:
            Tuple of (status, reason, requires_approval) where:
            - status: "safe", "blocked", or "unknown"
            - reason: Human-readable explanation
            - requires_approval: True if user approval is needed

        Raises:
            SecurityError: If command contains dangerous patterns
        """
        if not command or not command.strip():
            raise SecurityError("Empty command")

        command = command.strip()

        # Check for dangerous patterns first (most critical)
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in command:
                raise SecurityError(
                    f"Dangerous shell pattern detected: '{pattern}'. "
                    "Command chaining and redirection are not allowed."
                )

        # Parse the command to get the base command
        try:
            parts = shlex.split(command)
            if not parts:
                raise SecurityError("Invalid command syntax")
            base_command = parts[0]
        except ValueError as e:
            raise SecurityError(f"Invalid command syntax: {e}")

        # Check if command is blocked
        if base_command in cls.BLOCKED_COMMANDS:
            return (
                "blocked",
                f"Command '{base_command}' is blocked for security reasons",
                False
            )

        # Check if command is in safe list
        if base_command in cls.SAFE_COMMANDS:
            return (
                "safe",
                f"Command '{base_command}' is in the safe list",
                False
            )

        # Unknown command - requires user approval
        return (
            "unknown",
            f"Command '{base_command}' is not in the safe list",
            True
        )

    @classmethod
    def is_safe(cls, command: str) -> bool:
        """
        Quick check if a command is safe to execute.

        Args:
            command: The shell command to check

        Returns:
            bool: True if command is safe, False otherwise
        """
        try:
            status, _, _ = cls.validate_command(command)
            return status == "safe"
        except SecurityError:
            return False

    @classmethod
    def is_blocked(cls, command: str) -> bool:
        """
        Quick check if a command is blocked.

        Args:
            command: The shell command to check

        Returns:
            bool: True if command is blocked, False otherwise
        """
        try:
            status, _, _ = cls.validate_command(command)
            return status == "blocked"
        except SecurityError:
            return True  # Dangerous patterns are also considered blocked

    @classmethod
    def get_base_command(cls, command: str) -> str:
        """
        Extract the base command from a shell command string.

        Args:
            command: The full shell command

        Returns:
            str: The base command (first word)

        Raises:
            SecurityError: If command cannot be parsed
        """
        if not command or not command.strip():
            raise SecurityError("Empty command")

        try:
            parts = shlex.split(command.strip())
            if not parts:
                raise SecurityError("Invalid command syntax")
            return parts[0]
        except ValueError as e:
            raise SecurityError(f"Invalid command syntax: {e}")
