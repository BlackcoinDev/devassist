"""
Command registry for DevAssist.

This module provides a plugin-style command registration system that allows
commands to be registered with decorators and dispatched by name.
"""

import logging
from typing import Callable, Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class CommandRegistry:
    """
    Registry for slash commands.

    Commands are registered with a name and handler function.
    The registry handles dispatch, help text generation, and error handling.

    Usage:
        @CommandRegistry.register("help")
        def handle_help(args: List[str]) -> None:
            print("Help text here")

        # Dispatch
        CommandRegistry.dispatch("help", [])
    """

    _commands: Dict[str, Callable] = {}
    _descriptions: Dict[str, str] = {}
    _categories: Dict[str, List[str]] = {}

    @classmethod
    def register(
        cls,
        name: str,
        description: str = "",
        category: str = "general",
        aliases: Optional[List[str]] = None
    ) -> Callable:
        """
        Decorator to register a command handler.

        Args:
            name: Command name (without leading /)
            description: Help text for the command
            category: Category for grouping in help output
            aliases: Alternative names for the command

        Returns:
            Decorator function

        Example:
            @CommandRegistry.register("help", "Show available commands")
            def handle_help(args):
                ...
        """
        def decorator(func: Callable) -> Callable:
            cls._commands[name] = func
            cls._descriptions[name] = description

            # Track category
            if category not in cls._categories:
                cls._categories[category] = []
            cls._categories[category].append(name)

            # Register aliases
            if aliases:
                for alias in aliases:
                    cls._commands[alias] = func

            return func
        return decorator

    @classmethod
    def dispatch(cls, command: str, args: List[str]) -> bool:
        """
        Execute a registered command.

        Args:
            command: Command name (without leading /)
            args: Command arguments

        Returns:
            True if command was found and executed, False otherwise
        """
        handler = cls._commands.get(command)
        if handler is None:
            return False

        try:
            handler(args)
            return True
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            print(f"❌ Error executing command: {e}")
            return True  # Command was found, just errored

    @classmethod
    def get_commands(cls) -> Dict[str, str]:
        """
        Get all registered commands and their descriptions.

        Returns:
            Dict mapping command names to descriptions
        """
        return cls._descriptions.copy()

    @classmethod
    def get_categories(cls) -> Dict[str, List[str]]:
        """
        Get commands grouped by category.

        Returns:
            Dict mapping category names to lists of command names
        """
        return cls._categories.copy()

    @classmethod
    def has_command(cls, name: str) -> bool:
        """Check if a command is registered."""
        return name in cls._commands

    @classmethod
    def clear(cls) -> None:
        """Clear all registered commands. Useful for testing."""
        cls._commands.clear()
        cls._descriptions.clear()
        cls._categories.clear()


def register_command(
    name: str,
    description: str = "",
    category: str = "general",
    aliases: Optional[List[str]] = None
) -> Callable:
    """
    Convenience function for registering commands.

    This is equivalent to CommandRegistry.register() but reads better
    as a standalone decorator.

    Example:
        @register_command("help", "Show help", category="info")
        def handle_help(args):
            ...
    """
    return CommandRegistry.register(name, description, category, aliases)
