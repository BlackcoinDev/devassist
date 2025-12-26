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
Path security utilities for DevAssist.

Provides comprehensive path validation to prevent directory traversal
attacks and ensure file operations stay within sandboxed directories.
"""

import os

from src.security.exceptions import SecurityError


class PathSecurity:
    """
    Comprehensive path security validator to prevent path traversal attacks.

    Features:
    - Path traversal prevention
    - Directory sandboxing
    - File type validation
    - Size limits
    - Binary file detection

    All methods are class methods for stateless operation.
    """

    MAX_FILE_SIZE = 1024 * 1024  # 1MB limit

    DANGEROUS_PATTERNS = [
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
        "C:\\",
        "D:\\",
        "E:\\",
    ]

    @classmethod
    def validate_path(cls, user_path: str, base_dir: str | None = None) -> str:
        """
        Validate a user-provided path for security.

        Args:
            user_path: User-provided path
            base_dir: Base directory for sandboxing (defaults to current directory)

        Returns:
            str: Validated absolute path

        Raises:
            SecurityError: If path is invalid or unsafe
        """
        if not user_path:
            raise SecurityError("Empty path")

        # Use current directory as base if not specified
        if base_dir is None:
            base_dir = os.getcwd()

        # Convert to absolute path
        try:
            full_path = os.path.abspath(os.path.join(base_dir, user_path))
        except (TypeError, ValueError) as e:
            raise SecurityError(f"Invalid path: {e}")

        # Check for path traversal attempts
        if not full_path.startswith(base_dir):
            raise SecurityError(f"Path traversal attempt: {user_path}")

        # Check for dangerous patterns
        path_lower = user_path.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.lower() in path_lower:
                raise SecurityError(f"Dangerous path pattern detected: {user_path}")

        # Check if path exists (unless it's a new file for writing)
        if not os.path.exists(full_path):
            # For new files, check parent directory exists
            parent_dir = os.path.dirname(full_path)
            if parent_dir and not os.path.exists(parent_dir):
                raise SecurityError(f"Parent directory doesn't exist: {parent_dir}")

        return full_path

    @classmethod
    def validate_file_read(cls, file_path: str, base_dir: str | None = None) -> str:
        """
        Validate a file path for reading operations.

        Args:
            file_path: Path to file
            base_dir: Base directory for sandboxing

        Returns:
            str: Validated file path

        Raises:
            SecurityError: If file cannot be read safely
        """
        safe_path = cls.validate_path(file_path, base_dir)

        # Must be a file
        if not os.path.isfile(safe_path):
            raise SecurityError(f"Not a file: {file_path}")

        # Check file size
        try:
            file_size = os.path.getsize(safe_path)
            if file_size > cls.MAX_FILE_SIZE:
                raise SecurityError(
                    f"File too large: {file_size} bytes (max {cls.MAX_FILE_SIZE})"
                )
        except OSError as e:
            raise SecurityError(f"Cannot access file: {e}")

        # Security: Validate path using PathSecurity
        try:
            current_dir = os.getcwd()
            cls.validate_path(safe_path, current_dir)
        except SecurityError as e:
            raise SecurityError(f"Path security validation failed: {e}")

        # Check for binary files (basic detection)
        try:
            with open(safe_path, "rb") as f:
                header = f.read(1024)
                # Check for null bytes (common in binary files)
                if b"\x00" in header:
                    raise SecurityError("Binary file detected")
        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Cannot validate file content: {e}")

        return safe_path

    @classmethod
    def validate_file_write(cls, file_path: str, base_dir: str | None = None) -> str:
        """
        Validate a file path for writing operations.

        Args:
            file_path: Path to file
            base_dir: Base directory for sandboxing

        Returns:
            str: Validated file path

        Raises:
            SecurityError: If file cannot be written safely
        """
        safe_path = cls.validate_path(file_path, base_dir)

        # For directories, ensure we're not trying to write to a directory
        if os.path.exists(safe_path) and os.path.isdir(safe_path):
            raise SecurityError(f"Cannot write to directory: {file_path}")

        # Ensure parent directory exists
        parent_dir = os.path.dirname(safe_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except OSError as e:
                raise SecurityError(f"Cannot create directory: {e}")

        return safe_path

    @classmethod
    def validate_directory(
        cls, directory_path: str, base_dir: str | None = None
    ) -> str:
        """
        Validate a directory path.

        Args:
            directory_path: Path to directory
            base_dir: Base directory for sandboxing

        Returns:
            str: Validated directory path

        Raises:
            SecurityError: If directory is invalid
        """
        safe_path = cls.validate_path(directory_path, base_dir)

        # Must be a directory
        if not os.path.isdir(safe_path):
            raise SecurityError(f"Not a directory: {directory_path}")

        return safe_path
