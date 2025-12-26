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
Tool executors for DevAssist.

This module imports all tool executor modules to ensure they register
their tools with the ToolRegistry.

Import this module to make all tools available.
"""

# Import all executor modules (triggers registration)
from src.tools.executors import file_tools
from src.tools.executors import knowledge_tools
from src.tools.executors import document_tools
from src.tools.executors import web_tools
from src.tools.executors import shell_tools
from src.tools.executors import git_tools
from src.tools.executors import system_tools

__all__ = [
    "file_tools",
    "knowledge_tools",
    "document_tools",
    "web_tools",
    "shell_tools",
    "git_tools",
    "system_tools",
]
