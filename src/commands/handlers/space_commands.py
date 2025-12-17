#!/usr/bin/env python3
"""
Space Management Commands - Manage workspace/collection spaces.

This module provides command handlers for creating, switching, and
managing isolated knowledge base workspaces.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.core.context import get_context
from src.vectordb import list_spaces, switch_space, delete_space, get_space_collection_name

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("space", "Manage workspaces", category="spaces")
def handle_space(args: List[str]) -> None:
    """Handle /space command."""
    ctx = get_context()

    space_cmd = " ".join(args) if args else ""

    if not space_cmd:
        # Show current space
        print(f"\nCurrent space: {ctx.current_space}")
        print(f"Collection: {get_space_collection_name(ctx.current_space)}")
        print("\nUsage:")
        print("  /space list                    - List all spaces")
        print("  /space create <name>           - Create new space")
        print("  /space switch <name>           - Switch to space")
        print("  /space delete <name>           - Delete space")
        print("  /space current                 - Show current space\n")
        return

    if space_cmd == "list":
        spaces = list_spaces()
        print(f"\nAvailable spaces ({len(spaces)}):")
        for space in spaces:
            marker = " ← current" if space == ctx.current_space else ""
            print(f"  • {space}{marker}")
        print()

    elif space_cmd == "current":
        print(f"\nCurrent space: {ctx.current_space}")
        print(f"Collection: {get_space_collection_name(ctx.current_space)}\n")

    elif space_cmd.startswith("create "):
        new_space = space_cmd[7:].strip()
        if not new_space:
            print("\n❌ Usage: /space create <name>\n")
            return

        if new_space in list_spaces():
            print(f"\n❌ Space '{new_space}' already exists\n")
            return

        if switch_space(new_space):
            print(f"\n✅ Created and switched to space: {new_space}")
            print(f"Collection: {get_space_collection_name(new_space)}\n")
        else:
            print(f"\n❌ Failed to create space: {new_space}\n")

    elif space_cmd.startswith("switch "):
        target_space = space_cmd[7:].strip()
        if not target_space:
            print("\n❌ Usage: /space switch <name>\n")
            return

        if target_space not in list_spaces():
            print(f"\n❌ Space '{target_space}' does not exist")
            print(f"Use '/space create {target_space}' to create it first\n")
            return

        if switch_space(target_space):
            print(f"\n✅ Switched to space: {target_space}")
            print(f"Collection: {get_space_collection_name(target_space)}\n")
        else:
            print(f"\n❌ Failed to switch to space: {target_space}\n")

    elif space_cmd.startswith("delete "):
        target_space = space_cmd[7:].strip()
        if not target_space:
            print("\n❌ Usage: /space delete <name>\n")
            return

        if target_space == "default":
            print("\n❌ Cannot delete the default space\n")
            return

        if target_space not in list_spaces():
            print(f"\n❌ Space '{target_space}' does not exist\n")
            return

        # Confirm deletion
        confirm = input(
            f"Are you sure you want to delete space '{target_space}' and all its data? (yes/no): "
        )
        if confirm.lower() not in ["yes", "y"]:
            print("\n❌ Deletion cancelled\n")
            return

        if delete_space(target_space):
            print(f"\n✅ Deleted space: {target_space}\n")
        else:
            print(f"\n❌ Failed to delete space: {target_space}\n")

    else:
        print(f"\n❌ Unknown space command: {space_cmd}")
        print("Use '/space' for help\n")


__all__ = ["handle_space"]
