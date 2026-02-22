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

"""Security utilities for path validation and sanitization.

This module provides unified security functions that can be used across
the codebase to prevent path traversal attacks and validate file operations.
"""

import os
from typing import Optional


def validate_path(user_path: str, base_dir: Optional[str] = None) -> bool:
    """Validate that a user-provided path is safe and within allowed boundaries.

    Args:
        user_path: User-provided path to validate
        base_dir: Base directory for sandboxing (defaults to current directory)

    Returns:
        bool: True if path is valid, False otherwise
    """
    if not user_path:
        return False

    # Use current directory as base if not specified
    if base_dir is None:
        base_dir = os.getcwd()

    base_dir = os.path.abspath(base_dir)

    try:
        # Convert to absolute path and normalize
        full_path = os.path.abspath(os.path.join(base_dir, user_path))
    except (TypeError, ValueError):
        return False

    # Check for path traversal attempts
    if not full_path.startswith(base_dir):
        return False

    # Check for dangerous patterns
    dangerous_patterns = [
        "..",
        "../",
        "/../",
        "\\..\\",
        "~",
        "/~",
        "\\~",
        "/etc/",
        "/proc/",
        "/dev/",
    ]
    path_lower = user_path.lower()
    for pattern in dangerous_patterns:
        if pattern in path_lower:
            return False

    return True


def sanitize_path(user_path: str, base_dir: Optional[str] = None) -> str:
    """Sanitize and return a safe path.

    Args:
        user_path: User-provided path
        base_dir: Base directory for sandboxing (defaults to current directory)

    Returns:
        str: Sanitized absolute path

    Raises:
        ValueError: If path is invalid or unsafe
    """
    if not user_path:
        raise ValueError("Empty path")

    if not validate_path(user_path, base_dir):
        raise ValueError(f"Invalid or unsafe path: {user_path}")

    if base_dir is None:
        base_dir = os.getcwd()

    return os.path.abspath(os.path.join(base_dir, user_path))


def validate_command(command: str) -> bool:
    """Validate that a command is safe to execute.

    Args:
        command: Command string to validate

    Returns:
        bool: True if command is valid, False otherwise
    """
    if not command or not isinstance(command, str):
        return False

    # Check for dangerous patterns in commands
    dangerous_patterns = [
        ";",
        "&&",
        "||",
        "|",
        "`",
        "$",
        "(",
        ")",
        ">",
        "<",
        "&",
        "*",
        "?",
        "[",
        "]",
        "{",
        "}",
    ]

    for pattern in dangerous_patterns:
        if pattern in command:
            return False

    return True


__all__ = [
    "validate_path",
    "sanitize_path",
    "validate_command",
]
