"""
Command handlers for DevAssist.

This module imports all command handler modules to ensure they register
their commands with the CommandRegistry.

Import this module to make all commands available.
"""

# Import all handler modules to trigger registration
# Each module uses @CommandRegistry.register() decorator which registers on import
from src.commands.handlers import help_commands
from src.commands.handlers import memory_commands
from src.commands.handlers import database_commands
from src.commands.handlers import learning_commands
from src.commands.handlers import config_commands
from src.commands.handlers import space_commands
from src.commands.handlers import file_commands
from src.commands.handlers import export_commands

__all__ = [
    "help_commands",
    "memory_commands",
    "database_commands",
    "learning_commands",
    "config_commands",
    "space_commands",
    "file_commands",
    "export_commands",
]
