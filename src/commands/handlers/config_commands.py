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
Configuration Commands - Control application behavior settings.

This module provides command handlers for configuring context integration
and learning behavior modes.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.core.context import get_context, set_context_mode, set_learning_mode
from src.tools.approval import ToolApprovalManager

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


@CommandRegistry.register("approve", "Set tool approval mode (ask, always, never)", category="config")
def handle_approve(args: List[str]) -> None:
    """Handle /approve command."""
    manager = ToolApprovalManager()

    if not args or len(args) < 2:
        print("\n🛡️ Tool Approval Management")
        print("Usage: /approve <tool_name> <mode>")
        print("Modes: always, ask, never, auto-conservative, auto-permissive")
        print("\nExample: /approve shell_execute ask")
        print("Example: /approve read_file always")

        # List current custom rules
        if manager.approvals:
            print("\n📋 Custom Rules:")
            for tool, mode in manager.approvals.items():
                print(f"  - {tool}: {mode}")
        print()
        return

    tool_name = args[0]
    mode = args[1].lower()

    if manager.set_policy(tool_name, mode):
        print(f"\n✅ Approval policy for '{tool_name}' set to: {mode}\n")
    else:
        print(f"\n❌ Failed to set policy. Valid modes: always, ask, never, auto-conservative, auto-permissive\n")


@CommandRegistry.register("context", "Control context integration", category="config")
def handle_context(args: List[str]) -> None:
    """Handle /context command."""
    ctx = get_context()

    if not args:
        print(f"\n🎯 Current context mode: {ctx.context_mode}")
        print("Options: auto, on, off")
        print("- auto: AI decides when to include context")
        print("- on: Always include available context")
        print("- off: Never include context from knowledge base")
        print()
        return

    mode = args[0].lower()
    if mode in ["auto", "on", "off"]:
        set_context_mode(mode)
        print(f"\n✅ Context mode set to: {mode}\n")
    else:
        print(f"\n❌ Invalid context mode: {mode}")
        print("Valid options: auto, on, off\n")


@CommandRegistry.register("learning", "Control learning behavior", category="config")
def handle_learning(args: List[str]) -> None:
    """Handle /learning command."""
    ctx = get_context()

    if not args:
        print(f"\n🧠 Current learning mode: {ctx.learning_mode}")
        print("Options: normal, strict, off")
        print("- normal: Balanced learning with context integration")
        print("- strict: Minimal context, focused on explicit learning")
        print("- off: Disable all learning and context features")
        print()
        return

    mode = args[0].lower()
    if mode in ["normal", "strict", "off"]:
        set_learning_mode(mode)
        print(f"\n✅ Learning mode set to: {mode}\n")
    else:
        print(f"\n❌ Invalid learning mode: {mode}")
        print("Valid options: normal, strict, off\n")


__all__ = ["handle_context", "handle_learning"]
