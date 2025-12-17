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

__all__ = ["file_tools", "knowledge_tools", "document_tools", "web_tools"]
