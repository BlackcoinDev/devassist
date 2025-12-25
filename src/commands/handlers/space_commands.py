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
Space Commands Handler - Command handlers for space management.

Provides slash commands for managing spaces:
- /space - Show current space
- /space list - List all spaces
- /space create - Create new space
- /space switch - Switch to different space
- /space delete - Delete a space
"""

import logging
from typing import List, Union

from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.vectordb.spaces import (
    list_spaces,
    ensure_space_collection,
    delete_space,
)

logger = logging.getLogger(__name__)


@CommandRegistry.register(
    "space",
    "Manage spaces (workspaces)",
    category="space",
    aliases=["sp"],
)
def handle_space(args: Union[str, List[str]]) -> None:
    """
    Handle space management commands.

    Usage:
        /space              - Show current space
        /space list         - List all available spaces
        /space create NAME  - Create a new space
        /space switch NAME  - Switch to a space
        /space delete NAME  - Delete a space

    Args:
        args: Command arguments as a string or list
    """
    ctx = get_context()

    # Convert list to string if needed
    if isinstance(args, list):
        args = " ".join(args)

    if not args or args.strip() == "":
        # Show current space
        print(f"Current space: {ctx.current_space}")
        return

    parts = args.strip().split()
    command = parts[0].lower() if parts else ""

    if command == "list":
        # List all spaces
        try:
            spaces = list_spaces()
            if not spaces:
                print("No spaces found. Create one with: `/space create <name>`")
                return

            current = ctx.current_space
            space_count = len(spaces)
            print(f"\nAvailable spaces ({space_count}):")
            for space in spaces:
                marker = "  ← current" if space == current else ""
                print(f"  • {space}{marker}")
            print()
        except Exception as e:
            logger.error(f"Failed to list spaces: {e}")
            print(f"Error listing spaces: {e}")

    elif command == "create":
        # Create new space
        if len(parts) < 2:
            print("Usage: `/space create <name>`")
            return

        space_name = parts[1]
        try:
            ensure_space_collection(space_name)
            ctx.current_space = space_name
            logger.info(f"Created space: {space_name}")
            print(f"Created and switched to space: {space_name}")
        except Exception as e:
            logger.error(f"Failed to create space: {e}")
            print(f"Error creating space: {e}")

    elif command == "switch":
        # Switch to space
        if len(parts) < 2:
            print("Usage: `/space switch <name>`")
            return

        space_name = parts[1]
        try:
            ctx.current_space = space_name
            print(f"Switched to space: {space_name}")
        except Exception as e:
            logger.error(f"Failed to switch space: {e}")
            print(f"Error switching space: {e}")

    elif command == "delete":
        # Delete space
        if len(parts) < 2:
            print("Usage: `/space delete <name>`")
            return

        space_name = parts[1]
        if space_name == ctx.current_space:
            print("Cannot delete the current space. Switch to another space first.")
            return

        try:
            # Confirm deletion
            confirm = input(f"Delete space '{space_name}'? (yes/no): ").strip().lower()
            if confirm != "yes":
                print("Deletion cancelled.")
                return

            delete_space(space_name)
            logger.info(f"Deleted space: {space_name}")
            print(f"Deleted space: {space_name}")
        except Exception as e:
            logger.error(f"Failed to delete space: {e}")
            print(f"Error deleting space: {e}")

    else:
        print(f"Unknown space command: {command}")
        print("Usage: `/space [list|create|switch|delete] [name]`")


__all__ = ["handle_space"]
