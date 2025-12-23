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
File Operation Commands - Read, write, and list files.

This module provides command handlers for secure file operations
within the current working directory.
"""

import os
from typing import List
from src.commands.registry import CommandRegistry

__all__ = [
    "handle_read",
    "handle_write",
    "handle_list",
    "handle_pwd",
]

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("read", "Read file contents", category="files")
def handle_read(args: List[str]) -> None:
    """Handle /read command to read file contents."""
    file_path = " ".join(args) if args else ""

    if not file_path:
        print("\n❌ Usage: /read <file_path>")
        print("Example: /read README.md\n")
        return

    try:
        # Security: Only allow reading files in current directory
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        if not full_path.startswith(current_dir):
            print("\n❌ Access denied: Cannot read files outside current directory")
            print(f"Current directory: {current_dir}\n")
            return

        if not os.path.exists(full_path):
            print(f"\n❌ File not found: {file_path}\n")
            return

        if not os.path.isfile(full_path):
            print(f"\n❌ Not a file: {file_path}\n")
            return

        # Check file size (limit to 1MB)
        file_size = os.path.getsize(full_path)
        if file_size > 1024 * 1024:  # 1MB limit
            print(f"\n❌ File too large: {file_size} bytes (max 1MB)")
            print("Use a text editor to view large files\n")
            return

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        print(f"\n📄 File: {file_path}")
        print(f"📊 Size: {file_size} bytes")
        print("-" * 50)
        print(content)
        print("-" * 50)
        print("✅ File read successfully\n")

    except UnicodeDecodeError:
        print(f"\n❌ Cannot read binary file: {file_path}")
        print("This appears to be a binary file.\n")
    except Exception as e:
        print(f"\n❌ Failed to read file: {e}\n")


@CommandRegistry.register("write", "Write to file", category="files")
def handle_write(args: List[str]) -> None:
    """Handle /write command to write content to a file."""
    args_str = " ".join(args) if args else ""

    if not args_str:
        print("\n❌ Usage: /write <file_path> <content>")
        print("Example: /write notes.txt This is my note\n")
        return

    # Split on first space to separate file path from content
    parts = args_str.split(" ", 1)
    if len(parts) < 2:
        print("\n❌ Usage: /write <file_path> <content>")
        print("Content is required\n")
        return

    file_path, content = parts

    try:
        # Security: Only allow writing files in current directory
        current_dir = os.getcwd()
        full_path = os.path.abspath(file_path)

        if not full_path.startswith(current_dir):
            print("\n❌ Access denied: Cannot write files outside current directory")
            print(f"Current directory: {current_dir}\n")
            return

        # Create directory if it doesn't exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"\n✅ File written: {file_path}")
        print(f"📊 Content length: {len(content)} characters\n")

    except Exception as e:
        print(f"\n❌ Failed to write file: {e}\n")


@CommandRegistry.register("list", "List directory contents", category="files")
def handle_list(args: List[str]) -> None:
    """Handle /list command to list directory contents."""
    dir_path = " ".join(args) if args else ""

    try:
        if not dir_path:
            target_dir = os.getcwd()
        else:
            # Security: Only allow listing directories in current directory
            current_dir = os.getcwd()
            full_path = os.path.abspath(dir_path)

            if not full_path.startswith(current_dir):
                print(
                    "\n❌ Access denied: Cannot list directories outside current directory"
                )
                print(f"Current directory: {current_dir}\n")
                return

            if not os.path.exists(full_path):
                print(f"\n❌ Directory not found: {dir_path}\n")
                return

            if not os.path.isdir(full_path):
                print(f"\n❌ Not a directory: {dir_path}\n")
                return

            target_dir = full_path

        print(f"\n📁 Directory: {os.path.relpath(target_dir, os.getcwd()) or '.'}")
        print("-" * 50)

        items = os.listdir(target_dir)
        if not items:
            print("📂 (empty directory)")
        else:
            # Separate files and directories
            dirs = []
            files = []

            for item in sorted(items):
                full_item_path = os.path.join(target_dir, item)
                if os.path.isdir(full_item_path):
                    dirs.append(item + "/")
                else:
                    files.append(item)

            # Display directories first, then files
            for item in dirs + files:
                print(f"  {item}")

        print("-" * 50)
        print(f"📊 Total items: {len(items)}\n")

    except Exception as e:
        print(f"\n❌ Failed to list directory: {e}\n")


@CommandRegistry.register("pwd", "Show current directory", category="files")
def handle_pwd(args: List[str]) -> None:
    """Handle /pwd command to show current working directory."""
    try:
        current_dir = os.getcwd()
        print(f"\n📂 Current directory: {current_dir}\n")
    except Exception as e:
        print(f"\n❌ Failed to get current directory: {e}\n")


__all__ = ["handle_read", "handle_write", "handle_list", "handle_pwd"]
