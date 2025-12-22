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
Shell Tools - Executors for shell command execution.

This module provides AI tool executors for secure shell command execution.
Shell execution is restricted to CLI mode only for security reasons.
Commands are validated against allowlist/blocklist before execution.
"""

import os
import logging
import subprocess
from typing import Dict, Any

from src.tools.registry import ToolRegistry
from src.security.shell_security import ShellSecurity
from src.security.exceptions import SecurityError

logger = logging.getLogger(__name__)

# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

SHELL_EXECUTE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "shell_execute",
        "description": (
            "Execute a shell command in the current directory. "
            "Only available in CLI mode. Commands are validated for security. "
            "Dangerous commands (rm, sudo, etc.) are blocked. "
            "Use for running scripts, build tools, git commands, etc."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Command timeout in seconds (default: 30, max: 300)",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _is_gui_mode() -> bool:
    """
    Check if running in GUI mode.

    Returns:
        bool: True if in GUI mode, False if in CLI mode
    """
    return os.getenv("DEVASSIST_INTERFACE", "cli").lower() == "gui"


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("shell_execute", SHELL_EXECUTE_DEFINITION)
def execute_shell(command: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a shell command with security validation.

    Security measures:
    1. CLI mode only - blocked in GUI mode
    2. Command validation via ShellSecurity
    3. Dangerous patterns blocked (&&, ||, ;, pipes, etc.)
    4. Blocked commands never execute (rm, sudo, etc.)
    5. Timeout enforcement

    Args:
        command: The shell command to execute
        timeout: Command timeout in seconds (default: 30, max: 300)

    Returns:
        Dict with success status, stdout, stderr, and return_code
    """
    # Check interface mode
    if _is_gui_mode():
        return {
            "error": "Shell execution is disabled in GUI mode for security reasons. "
                     "Please use the CLI interface for shell commands."
        }

    # Validate command is not empty
    if not command or not command.strip():
        return {"error": "Empty command"}

    command = command.strip()

    # Validate timeout
    if timeout < 1:
        timeout = 30
    elif timeout > 300:
        timeout = 300

    # Security validation
    try:
        status, reason, requires_approval = ShellSecurity.validate_command(command)
    except SecurityError as e:
        logger.warning(f"Shell command blocked: {command} - {e}")
        return {"error": str(e)}

    # Handle blocked commands
    if status == "blocked":
        logger.warning(f"Blocked command: {command} - {reason}")
        return {"error": reason}

    # Log unknown commands (requires user approval via tool approval system)
    if status == "unknown":
        logger.info(f"Unknown command (may require approval): {command}")

    # Execute the command
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
            env=os.environ.copy(),
        )

        # Truncate output if too long (max 50KB)
        max_output = 50 * 1024
        stdout = result.stdout
        stderr = result.stderr

        stdout_truncated = False
        stderr_truncated = False

        if len(stdout) > max_output:
            stdout = stdout[:max_output] + "\n... (output truncated)"
            stdout_truncated = True

        if len(stderr) > max_output:
            stderr = stderr[:max_output] + "\n... (output truncated)"
            stderr_truncated = True

        return {
            "success": result.returncode == 0,
            "command": command,
            "return_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "stdout_truncated": stdout_truncated,
            "stderr_truncated": stderr_truncated,
        }

    except subprocess.TimeoutExpired:
        logger.warning(f"Command timed out after {timeout}s: {command}")
        return {
            "error": f"Command timed out after {timeout} seconds",
            "command": command,
        }

    except Exception as e:
        logger.error(f"Error executing command '{command}': {e}")
        return {"error": str(e), "command": command}


__all__ = ["execute_shell"]
