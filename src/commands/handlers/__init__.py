"""
Command handlers for DevAssist.

This module imports all command handler modules to ensure they register
their commands with the CommandRegistry.

Import this module to make all commands available.
"""

# Import all handler modules to trigger registration
# Each module uses @register_command decorator which registers on import

# Note: These imports will be uncommented as handlers are extracted
# from src.commands.handlers import help_commands
# from src.commands.handlers import file_commands
# from src.commands.handlers import memory_commands
# from src.commands.handlers import space_commands
# from src.commands.handlers import learn_commands
# from src.commands.handlers import config_commands
