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
Tools module for DevAssist.

This module provides a AI tool system including:
- Tool registry for registration and execution
- Tool definitions for LLM binding
- Individual tool executor implementations

Import this module to make all tools available for AI tool calling.
"""

from src.tools.registry import ToolRegistry, register_tool

# Import all tool executors to trigger auto-registration
# Each executor module uses @ToolRegistry.register() decorator which registers on import
from src.tools.executors import file_tools
from src.tools.executors import knowledge_tools
from src.tools.executors import document_tools
from src.tools.executors import web_tools
from src.tools.executors import shell_tools
from src.tools.executors import git_tools
from src.tools.executors import system_tools

# Use the imported modules to prevent "unused import" warnings
# Reference the modules so they're marked as "used"
_tool_modules = {
    "file": file_tools,
    "knowledge": knowledge_tools,
    "document": document_tools,
    "web": web_tools,
    "shell": shell_tools,
    "git": git_tools,
    "system": system_tools,
}

__all__ = [
    "ToolRegistry",
    "register_tool",
]
