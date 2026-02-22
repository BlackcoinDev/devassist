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

"""Subprocess utilities for safe command execution.

This module provides unified subprocess execution with consistent
error handling, timeouts, and security checks.
"""

import os
import subprocess
from typing import List, Optional, Dict, Any


def get_safe_env() -> Dict[str, str]:
    """Get sanitized environment variables for subprocess execution.

    Returns:
        Dict[str, str]: Safe environment variables
    """
    safe_vars = {"PATH", "HOME", "LANG", "TERM", "SHELL", "USER", "PWD"}
    return {k: v for k, v in os.environ.items() if k in safe_vars}


def run_command(
    command: List[str],
    cwd: Optional[str] = None,
    timeout: int = 60,
    capture_output: bool = True,
) -> Dict[str, Any]:
    """Run a command with consistent error handling and security.

    Args:
        command: Command as list of arguments (e.g., ["git", "status"])
        cwd: Working directory for command execution
        timeout: Timeout in seconds (default: 60)
        capture_output: Whether to capture stdout/stderr

    Returns:
        Dict with keys: success (bool), returncode (int), stdout (str), stderr (str)
    """
    try:
        env = get_safe_env()

        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout if capture_output else "",
            "stderr": result.stderr if capture_output else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def run_git_command(
    args: List[str],
    cwd: Optional[str] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """Run a git command with validation.

    Args:
        args: Git command arguments (e.g., ["status", "--short"])
        cwd: Working directory (defaults to current directory)
        timeout: Timeout in seconds

    Returns:
        Dict with keys: success (bool), returncode (int), stdout (str), stderr (str)
    """
    safe_git_commands = {
        "status",
        "diff",
        "log",
        "show",
        "branch",
        "remote",
        "config",
    }

    if not args or args[0] not in safe_git_commands:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Unsafe or unsupported git command: {args[0] if args else 'none'}",
        }

    command = ["git"] + args
    return run_command(command, cwd=cwd, timeout=timeout)


__all__ = [
    "get_safe_env",
    "run_command",
    "run_git_command",
]
