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
from src.commands.handlers import git_commands
from src.commands.handlers import system_commands

__all__ = [
    "help_commands",
    "memory_commands",
    "database_commands",
    "learning_commands",
    "config_commands",
    "space_commands",
    "file_commands",
    "export_commands",
    "git_commands",
    "system_commands",
]
