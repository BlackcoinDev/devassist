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
File System Tools - Executors for file and directory operations.

This module provides AI tool executors for secure file system operations
including reading, writing, listing directories, and getting the current path.
All operations are sandboxed to the current working directory.
"""

import os
import logging
from typing import Dict, Any

from src.tools.registry import ToolRegistry
from src.core.utils import standard_error, standard_success
from src.core.security_utils import validate_path, sanitize_path
from src.security.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)


# =============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# =============================================================================

READ_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "read_file_content",
        "description": "Read the contents of a file in the current directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read (relative to current directory)",
                }
            },
            "required": ["file_path"],
        },
    },
}

WRITE_FILE_DEFINITION = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file in the current directory",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write (relative to current directory)",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}

LIST_DIRECTORY_DEFINITION = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List contents of a directory in the current workspace",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {
                    "type": "string",
                    "description": "Path to directory to list (optional, defaults to current directory)",
                    "default": ".",
                }
            },
        },
    },
}

GET_CURRENT_DIRECTORY_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_current_directory",
        "description": "Get the current working directory path",
        "parameters": {"type": "object", "properties": {}},
    },
}


# =============================================================================
# TOOL EXECUTORS
# =============================================================================


@ToolRegistry.register("read_file_content", READ_FILE_DEFINITION)
def execute_read_file(file_path: str) -> Dict[str, Any]:
    """
    Execute file reading tool with security checks.

    Args:
        file_path: Path to file (relative to current directory)

    Returns:
        Dict with success status, content, and file metadata
    """
    try:
        logger.debug("🔧 read_file_content: Starting")
        logger.debug(f"   File path: {file_path}")

        # Security check - use shared security utility
        if not validate_path(file_path):
            logger.warning("🚫 read_file_content: Blocked - Invalid or unsafe path")
            get_audit_logger().log_path_access_denied(
                file_path, "read", "Path validation failed"
            )
            return standard_error(
                "Access denied: Cannot read files outside current directory"
            )

        full_path = sanitize_path(file_path)

        if not os.path.exists(full_path):
            logger.warning(f"🚫 read_file_content: File not found - {file_path}")
            return standard_error(f"File not found: {file_path}")

        if not os.path.isfile(full_path):
            logger.warning(f"🚫 read_file_content: Not a file - {file_path}")
            return standard_error(f"Not a file: {file_path}")

        # Size check
        file_size = os.path.getsize(full_path)
        logger.debug(f"📄 read_file_content: File size: {file_size} bytes")

        if file_size > 1024 * 1024:  # 1MB limit
            logger.warning(
                f"🚫 read_file_content: File too large - {file_size} bytes (max 1MB)"
            )
            return standard_error(f"File too large: {file_size} bytes (max 1MB)")

        # Content check
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.warning(
                f"🚫 read_file_content: Cannot read binary file - {file_path}"
            )
            return standard_error("Cannot read binary file")
        except Exception as e:
            logger.error(f"❌ read_file_content: Error reading file - {e}")
            return standard_error(str(e))

        logger.debug(
            f"✅ read_file_content: Successfully read {len(content)} chars from {file_path}"
        )
        return standard_success(
            {"file_path": file_path, "content": content, "size": file_size}
        )

    except Exception as e:
        logger.error(f"❌ read_file_content: Error reading file - {e}")
        return standard_error(str(e))


@ToolRegistry.register("write_file", WRITE_FILE_DEFINITION)
def execute_write_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Execute file writing tool with security checks.

    Args:
        file_path: Path to file (relative to current directory)
        content: Content to write

    Returns:
        Dict with success status and file metadata
    """
    try:
        # Security check - use shared security utility
        if not validate_path(file_path):
            get_audit_logger().log_path_access_denied(
                file_path, "write", "Path validation failed"
            )
            return {
                "error": "Access denied: Cannot write files outside current directory"
            }

        full_path = sanitize_path(file_path)

        # Create directory if needed
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        return standard_success({"file_path": file_path, "size": len(content)})

    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return standard_error(str(e))


@ToolRegistry.register("list_directory", LIST_DIRECTORY_DEFINITION)
def execute_list_directory(directory_path: str = ".") -> Dict[str, Any]:
    """
    Execute directory listing tool with security checks.

    Args:
        directory_path: Path to directory (default: current directory)

    Returns:
        Dict with success status and directory contents
    """
    try:
        # Security check - use shared security utility
        if not validate_path(directory_path):
            get_audit_logger().log_path_access_denied(
                directory_path, "list", "Path validation failed"
            )
            return {
                "error": "Access denied: Cannot list directories outside current directory"
            }

        full_path = sanitize_path(directory_path)

        if not os.path.exists(full_path):
            return standard_error(f"Directory not found: {directory_path}")

        if not os.path.isdir(full_path):
            return {"error": f"Not a directory: {directory_path}"}

        items = os.listdir(full_path)
        dirs = []
        files = []

        for item in sorted(items):
            full_item_path = os.path.join(full_path, item)
            if os.path.isdir(full_item_path):
                dirs.append(item + "/")
            else:
                files.append(item)

        return {
            "success": True,
            "directory": os.path.relpath(full_path, os.getcwd()) or ".",
            "contents": dirs + files,
            "total_items": len(items),
        }

    except Exception as e:
        logger.error(f"Error listing directory {directory_path}: {e}")
        return standard_error(str(e))


@ToolRegistry.register("get_current_directory", GET_CURRENT_DIRECTORY_DEFINITION)
def execute_get_current_directory() -> Dict[str, Any]:
    """
    Execute current directory tool.

    Returns:
        Dict with success status and current directory path
    """
    try:
        return standard_success({"current_directory": os.getcwd()})
    except Exception as e:
        logger.error(f"Error getting current directory: {e}")
        return standard_error(str(e))


__all__ = [
    "execute_read_file",
    "execute_write_file",
    "execute_list_directory",
    "execute_get_current_directory",
]
