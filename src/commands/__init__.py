"""
Commands module for DevAssist.

This module provides a plugin-style command system with:
- Command registry for registration and dispatch
- Organized handlers by category (file, memory, space, etc.)
- Consistent error handling and output formatting
"""

from src.commands.registry import CommandRegistry, register_command
# Import handlers to trigger registration
from src.commands import handlers  # noqa: F401

__all__ = [
    "CommandRegistry",
    "register_command",
]
