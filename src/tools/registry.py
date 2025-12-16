"""
Tool registry for DevAssist.

This module provides a plugin-style tool registration system that allows
AI tools to be registered with decorators and dispatched by name.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for AI tools.

    Tools are registered with a name, definition (for LLM binding), and executor.
    The registry handles dispatch, definition generation, and error handling.

    Usage:
        @ToolRegistry.register("read_file", READ_FILE_DEFINITION)
        def execute_read_file(file_path: str) -> dict:
            ...

        # Execute
        result = ToolRegistry.execute("read_file", {"file_path": "test.txt"})

        # Get definitions for LLM binding
        definitions = ToolRegistry.get_definitions()
    """

    _tools: Dict[str, Callable] = {}
    _definitions: Dict[str, Dict] = {}

    @classmethod
    def register(cls, name: str, definition: Optional[Dict] = None) -> Callable:
        """
        Decorator to register a tool executor.

        Args:
            name: Tool name (matches function name in LLM tool call)
            definition: OpenAI function definition for LLM binding

        Returns:
            Decorator function

        Example:
            @ToolRegistry.register("read_file", READ_FILE_DEFINITION)
            def execute_read_file(file_path: str) -> dict:
                return {"content": "..."}
        """
        def decorator(func: Callable) -> Callable:
            cls._tools[name] = func
            if definition:
                cls._definitions[name] = definition
            return func
        return decorator

    @classmethod
    def execute(cls, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool.

        Args:
            name: Tool name
            args: Tool arguments as dictionary

        Returns:
            Tool result dictionary
        """
        executor = cls._tools.get(name)
        if executor is None:
            return {"error": f"Unknown tool: {name}"}

        try:
            return executor(**args)
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}")
            return {"error": str(e)}

    @classmethod
    def execute_tool_call(cls, tool_call: Any) -> Dict[str, Any]:
        """
        Execute a tool call from the LLM.

        Args:
            tool_call: LangChain tool call object with name and args

        Returns:
            Tool result dictionary
        """
        try:
            name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
            args_raw = tool_call.get("args") if isinstance(tool_call, dict) else tool_call.args

            # Parse args if string
            if isinstance(args_raw, str):
                args = json.loads(args_raw)
            else:
                args = args_raw or {}

            return cls.execute(name, args)

        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON arguments: {e}"}
        except Exception as e:
            logger.error(f"Error processing tool call: {e}")
            return {"error": str(e)}

    @classmethod
    def get_definitions(cls) -> List[Dict]:
        """
        Get all tool definitions for LLM binding.

        Returns:
            List of OpenAI function definitions
        """
        return list(cls._definitions.values())

    @classmethod
    def get_tool_names(cls) -> List[str]:
        """Get list of registered tool names."""
        return list(cls._tools.keys())

    @classmethod
    def has_tool(cls, name: str) -> bool:
        """Check if a tool is registered."""
        return name in cls._tools

    @classmethod
    def clear(cls) -> None:
        """Clear all registered tools. Useful for testing."""
        cls._tools.clear()
        cls._definitions.clear()


def register_tool(name: str, definition: Optional[Dict] = None) -> Callable:
    """
    Convenience function for registering tools.

    This is equivalent to ToolRegistry.register() but reads better
    as a standalone decorator.

    Example:
        @register_tool("read_file", READ_FILE_DEFINITION)
        def execute_read_file(file_path: str) -> dict:
            ...
    """
    return ToolRegistry.register(name, definition)
