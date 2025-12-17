#!/usr/bin/env python3
"""
Configuration Commands - Control application behavior settings.

This module provides command handlers for configuring context integration
and learning behavior modes.
"""

from typing import List
from src.commands.registry import CommandRegistry
from src.core.context import get_context, set_context_mode, set_learning_mode

# =============================================================================
# COMMAND HANDLERS
# =============================================================================


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
