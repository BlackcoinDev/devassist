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
from pathlib import Path
from typing import Dict, Any

from src.tools.registry import ToolRegistry
from src.security.shell_security import ShellSecurity
from src.security.exceptions import SecurityError
from src.security.audit_logger import get_audit_logger
from src.core.utils import standard_error
from src.core.constants import (
    SHELL_DEFAULT_TIMEOUT,
    SHELL_MAX_TIMEOUT,
    SHELL_MAX_OUTPUT_SIZE,
    SAFE_ENV_VARS,
)
from src.core.subprocess_utils import get_safe_env

logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS
# =============================================================================

# Project root directory - captured at module import time
_PROJECT_ROOT: Path = Path.cwd().resolve()


def _validate_working_directory() -> Path:
    """
    Validate that the current working directory is within the project root.

    Returns:
        Path: The validated current working directory

    Raises:
        SecurityError: If cwd is outside the project root
    """
    cwd = Path.cwd().resolve()
    try:
        cwd.relative_to(_PROJECT_ROOT)
        return cwd
    except ValueError:
        # Log security violation
        get_audit_logger().log_cwd_violation(str(cwd), str(_PROJECT_ROOT))
        raise SecurityError(
            f"Shell execution blocked: Current directory '{cwd}' is outside "
            f"project root '{_PROJECT_ROOT}'. Shell commands are restricted "
            "to the project directory tree for security."
        )


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
                    "description": (
                        f"Command timeout in seconds (default: {SHELL_DEFAULT_TIMEOUT}, "
                        f"max: {SHELL_MAX_TIMEOUT})"
                    ),
                    "default": SHELL_DEFAULT_TIMEOUT,
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
def execute_shell(command: str, timeout: int = SHELL_DEFAULT_TIMEOUT) -> Dict[str, Any]:
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
    # Log tool start
    logger.debug("🔧 shell_execute: Starting execution")
    logger.debug(f"   Command: {command}")
    logger.debug(f"   Timeout: {timeout}s")

    # Check interface mode
    if _is_gui_mode():
        logger.warning("🚫 shell_execute: Blocked - GUI mode")
        return standard_error(
            "Shell execution is disabled in GUI mode for security reasons. "
            "Please use the CLI interface for shell commands."
        )

    # Validate command is not empty
    if not command or not command.strip():
        logger.warning("🚫 shell_execute: Blocked - Empty command")
        return standard_error("Empty command")

    command = command.strip()

    # Log command details
    logger.debug(f"🔧 shell_execute: Executing '{command}' with {timeout}s timeout")

    # Validate timeout
    if timeout < 1:
        logger.debug(
            f"⚠️ shell_execute: Timeout too low ({timeout}s), using default {SHELL_DEFAULT_TIMEOUT}s"
        )
        timeout = SHELL_DEFAULT_TIMEOUT
    elif timeout > SHELL_MAX_TIMEOUT:
        logger.debug(
            f"⚠️ shell_execute: Timeout too high ({timeout}s), using max {SHELL_MAX_TIMEOUT}s"
        )
        timeout = SHELL_MAX_TIMEOUT

    # Security validation
    try:
        status, reason, requires_approval = ShellSecurity.validate_command(command)
    except SecurityError as e:
        logger.warning(
            f"🚫 shell_execute: Security validation failed - {command} - {e}"
        )
        return standard_error(str(e))

    # Handle blocked commands
    if status == "blocked":
        logger.warning(f"🚫 shell_execute: Blocked command - {command} - {reason}")
        get_audit_logger().log_shell_blocked(command, reason)
        return standard_error(reason)

    # Log unknown commands (requires user approval via tool approval system)
    if status == "unknown":
        logger.info(
            f"🤔 shell_execute: Unknown command (may require approval) - {command}"
        )

    # Execute the command
    try:
        # Log security context
        logger.debug("🔒 shell_execute: Security validation passed")
        logger.debug(f"   Status: {status}, Approval required: {requires_approval}")

        # Split command into arguments for safer execution
        import shlex

        cmd_parts = shlex.split(command)

        logger.debug(f"🔧 shell_execute: Parsed command parts: {cmd_parts}")

        result = subprocess.run(
            cmd_parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=_validate_working_directory(),
            env=get_safe_env(),
        )

        # Log execution results
        logger.debug("✅ shell_execute: Command completed")
        logger.debug(f"   Return code: {result.returncode}")
        logger.debug(
            f"   Output length: stdout={len(result.stdout)} chars, stderr={len(result.stderr)} chars"
        )

        # Truncate output if too long (max 50KB)
        max_output = SHELL_MAX_OUTPUT_SIZE
        stdout = result.stdout
        stderr = result.stderr

        stdout_truncated = False
        stderr_truncated = False

        if len(stdout) > max_output:
            stdout = stdout[:max_output] + "\n... (output truncated)"
            stdout_truncated = True
            logger.debug(f"📊 shell_execute: Output truncated at {max_output} chars")

        if len(stderr) > max_output:
            stderr = stderr[:max_output] + "\n... (output truncated)"
            stderr_truncated = True
            logger.debug(
                f"📊 shell_execute: Error output truncated at {max_output} chars"
            )

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
        logger.warning(
            f"⏰ shell_execute: Command timed out after {timeout}s - {command}"
        )
        return standard_error(
            f"Command timed out after {timeout} seconds", {"command": command}
        )

    except Exception as e:
        logger.error(f"❌ shell_execute: Error executing command '{command}' - {e}")
        return standard_error(str(e), {"command": command})


__all__ = ["execute_shell"]
