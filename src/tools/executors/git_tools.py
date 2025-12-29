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
Git Tools - Executors for git repository operations.

This module provides AI tool executors for git operations including
status, diff, and log. All operations are read-only for safety.
"""

import os
import logging
import subprocess
from typing import Dict, Any, Optional, List

from src.tools.registry import ToolRegistry
from src.core.utils import standard_error, standard_success
from src.core.constants import GIT_DEFAULT_TIMEOUT, GIT_DIFF_TIMEOUT, GIT_DIFF_MAX_SIZE

logger = logging.getLogger(__name__)

# =============================================================================
# CONSTANTS
# =============================================================================

# Safe git commands that are allowed (read-only operations)
# Note: 'show' is intentionally excluded as it can expose file contents
SAFE_GIT_COMMANDS = {"status", "diff", "log", "rev-parse", "branch"}


def _validate_git_args(args: List[str]) -> None:
    """
    Validate git command arguments for security.

    Args:
        args: Git command arguments

    Raises:
        SecurityError: If command or arguments are unsafe
    """
    if not args:
        raise ValueError("Empty git command arguments")

    command = args[0]
    if command not in SAFE_GIT_COMMANDS:
        from src.security.exceptions import SecurityError

        raise SecurityError(f"Unsafe git command: {command}")


def _sanitize_file_path(file_path: str) -> str:
    """
    Sanitize file path to prevent directory traversal attacks.

    Args:
        file_path: The file path to sanitize

    Returns:
        Sanitized file path

    Raises:
        SecurityError: If path contains dangerous patterns
    """
    import os.path
    from src.security.exceptions import SecurityError

    # Basic path traversal checks
    if ".." in file_path or file_path.startswith("/"):
        raise SecurityError(f"Unsafe file path: {file_path}")

    # Normalize path
    normalized = os.path.normpath(file_path)

    # Ensure it's still safe after normalization
    if normalized.startswith("/") or ".." in normalized:
        raise SecurityError(f"Path traversal attempt: {file_path}")

    return normalized


# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

GIT_STATUS_DEFINITION = {
    "type": "function",
    "function": {
        "name": "git_status",
        "description": (
            "Get the current git repository status. "
            "Shows staged, unstaged, and untracked files. "
            "Returns structured data about the working tree state."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

GIT_DIFF_DEFINITION = {
    "type": "function",
    "function": {
        "name": "git_diff",
        "description": (
            "Show git diff for changes in the repository. "
            "Can show staged or unstaged changes, optionally for a specific file."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Optional file path to show diff for (relative to repo root)",
                },
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes (--staged). Default: false (unstaged)",
                    "default": False,
                },
            },
        },
    },
}

GIT_LOG_DEFINITION = {
    "type": "function",
    "function": {
        "name": "git_log",
        "description": (
            "Show git commit history. "
            "Returns recent commits with hash, author, date, and message. "
            "Can optionally filter by file path."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of commits to show (default: 10, max: 100)",
                    "default": 10,
                },
                "file_path": {
                    "type": "string",
                    "description": "Optional file path to show history for",
                },
            },
        },
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _run_git_command(
    args: List[str], timeout: int = GIT_DEFAULT_TIMEOUT
) -> tuple[bool, str, str]:
    """
    Run a git command safely.

    Args:
        args: Git command arguments (without 'git' prefix)
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success, stdout, stderr)
    """
    # Validate git command arguments
    _validate_git_args(args)

    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd(),
        )
        return (result.returncode == 0, result.stdout, result.stderr)
    except subprocess.TimeoutExpired:
        return (False, "", f"Git command timed out after {timeout} seconds")
    except FileNotFoundError:
        return (False, "", "Git is not installed or not in PATH")
    except Exception as e:
        return (False, "", str(e))


def _is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    success, _, _ = _run_git_command(["rev-parse", "--git-dir"])
    return success


def _parse_status_porcelain(output: str) -> Dict[str, List[str]]:
    """
    Parse git status --porcelain output into structured data.

    Returns:
        Dict with 'staged', 'unstaged', 'untracked' lists
    """
    staged = []
    unstaged = []
    untracked = []

    for line in output.strip().split("\n"):
        if not line:
            continue

        # Status is first 2 characters
        if len(line) < 3:
            continue

        index_status = line[0]
        worktree_status = line[1]
        filename = line[3:]

        # Untracked files
        if index_status == "?" and worktree_status == "?":
            untracked.append(filename)
        else:
            # Staged changes (non-space in index column)
            if index_status not in (" ", "?"):
                staged.append(f"{index_status} {filename}")
            # Unstaged changes (non-space in worktree column)
            if worktree_status not in (" ", "?"):
                unstaged.append(f"{worktree_status} {filename}")

    return {
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
    }


def _parse_log_output(output: str) -> List[Dict[str, str]]:
    """
    Parse git log output into structured data.

    Expects format: hash|author|date|subject
    """
    commits = []
    for line in output.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 3)
        if len(parts) >= 4:
            commits.append(
                {
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": parts[3],
                }
            )
    return commits


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("git_status", GIT_STATUS_DEFINITION)
def execute_git_status() -> Dict[str, Any]:
    """
    Execute git status and return structured results.

    Returns:
        Dict with success status and categorized file changes
    """
    # Check if in a git repo
    if not _is_git_repo():
        return standard_error("Not a git repository")

    # Get status
    success, stdout, stderr = _run_git_command(["status", "--porcelain"])

    if not success:
        return {"error": f"Git status failed: {stderr}"}

    # Parse the output
    status = _parse_status_porcelain(stdout)

    # Get branch name
    branch_success, branch_out, _ = _run_git_command(
        ["rev-parse", "--abbrev-ref", "HEAD"]
    )
    branch = branch_out.strip() if branch_success else "unknown"

    # Check if clean
    is_clean = not (status["staged"] or status["unstaged"] or status["untracked"])

    return {
        "success": True,
        "branch": branch,
        "is_clean": is_clean,
        "staged": status["staged"],
        "unstaged": status["unstaged"],
        "untracked": status["untracked"],
        "staged_count": len(status["staged"]),
        "unstaged_count": len(status["unstaged"]),
        "untracked_count": len(status["untracked"]),
    }


@ToolRegistry.register("git_diff", GIT_DIFF_DEFINITION)
def execute_git_diff(
    file_path: Optional[str] = None, staged: bool = False
) -> Dict[str, Any]:
    """
    Execute git diff and return the diff output.

    Args:
        file_path: Optional specific file to diff
        staged: Show staged changes (--staged)

    Returns:
        Dict with success status and diff content
    """
    # Check if in a git repo
    if not _is_git_repo():
        return standard_error("Not a git repository")

    # Build command
    args = ["diff"]
    if staged:
        args.append("--staged")
    if file_path:
        # Sanitize file path to prevent directory traversal
        safe_path = _sanitize_file_path(file_path)
        args.append("--")
        args.append(safe_path)

    # Run diff
    success, stdout, stderr = _run_git_command(args, timeout=GIT_DIFF_TIMEOUT)

    if not success:
        return standard_error(f"Git diff failed: {stderr}")

    # Check if there are changes
    if not stdout.strip():
        scope = "staged" if staged else "unstaged"
        file_scope = f" for '{file_path}'" if file_path else ""
        return standard_success(
            {
                "has_changes": False,
                "message": f"No {scope} changes{file_scope}",
                "diff": "",
            }
        )

    # Truncate if too long (max 100KB)
    max_size = GIT_DIFF_MAX_SIZE
    truncated = False
    diff = stdout
    if len(diff) > max_size:
        diff = diff[:max_size] + "\n... (diff truncated, too large)"
        truncated = True

    return {
        "success": True,
        "has_changes": True,
        "staged": staged,
        "file_path": file_path,
        "diff": diff,
        "truncated": truncated,
    }


@ToolRegistry.register("git_log", GIT_LOG_DEFINITION)
def execute_git_log(limit: int = 10, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute git log and return structured commit history.

    Args:
        limit: Maximum commits to return (default: 10, max: 100)
        file_path: Optional file to filter history by

    Returns:
        Dict with success status and commit list
    """
    # Check if in a git repo
    if not _is_git_repo():
        return standard_error("Not a git repository")

    # Validate limit
    if limit < 1:
        limit = 10
    elif limit > 100:
        limit = 100

    # Build command with custom format for easy parsing
    # Format: hash|author|date|subject
    format_str = "%h|%an|%ad|%s"
    args = [
        "log",
        f"-n{limit}",
        f"--format={format_str}",
        "--date=short",
    ]

    if file_path:
        # Sanitize file path to prevent directory traversal
        safe_path = _sanitize_file_path(file_path)
        args.append("--")
        args.append(safe_path)

    # Run log
    success, stdout, stderr = _run_git_command(args)

    if not success:
        return {"error": f"Git log failed: {stderr}"}

    # Parse the output
    commits = _parse_log_output(stdout)

    return {
        "success": True,
        "commit_count": len(commits),
        "file_path": file_path,
        "commits": commits,
    }


__all__ = [
    "execute_git_status",
    "execute_git_diff",
    "execute_git_log",
]
