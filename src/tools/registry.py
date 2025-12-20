# MIT License
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
Tool registry for DevAssist.

This module provides a plugin-style tool registration system that allows
AI tools to be registered with decorators and dispatched by name.
"""

import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_config():
    """Lazily get config to avoid circular imports."""
    try:
        from src.core.config import get_config
        return get_config()
    except Exception:
        return None


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
            cfg = _get_config()
            if cfg and cfg.show_tool_details:
                logger.debug(f"🔧 Registered tool: {name}")
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
        cfg = _get_config()

        executor = cls._tools.get(name)
        if executor is None:
            return {"error": f"Unknown tool: {name}"}

        if cfg and cfg.show_tool_details:
            # Truncate args for display
            args_str = str(args)[:100] + "..." if len(str(args)) > 100 else str(args)
            logger.info(f"🔧 Executing tool: {name}")
            logger.info(f"   📥 Args: {args_str}")

        try:
            start_time = time.time()
            result = executor(**args)
            elapsed = time.time() - start_time

            if cfg and cfg.show_tool_details:
                success = "error" not in result if isinstance(result, dict) else True
                status = "✅" if success else "❌"
                logger.info(f"   {status} Completed in {elapsed:.2f}s")

            return result
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
            Dictionary containing 'function_name' and 'result'
        """
        try:
            name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
            args_raw = tool_call.get("args") if isinstance(tool_call, dict) else tool_call.args

            if name is None:
                return {
                    "function_name": "unknown",
                    "result": {"error": "Tool call missing 'name' field"}
                }

            # Parse args if string
            if isinstance(args_raw, str):
                args = json.loads(args_raw)
            else:
                args = args_raw or {}

            result = cls.execute(name, args)
            return {
                "function_name": name,
                "result": result
            }

        except json.JSONDecodeError as e:
            return {
                "function_name": "unknown",
                "result": {"error": f"Invalid JSON arguments: {e}"}
            }
        except Exception as e:
            logger.error(f"Error processing tool call: {e}")
            return {
                "function_name": "unknown",
                "result": {"error": str(e)}
            }

    @classmethod
    def get_definitions(cls) -> List[Dict]:
        """
        Get all tool definitions for LLM binding.

        Returns:
            List of OpenAI function definitions (deep copies to prevent modification)
        """
        import copy
        return [copy.deepcopy(definition) for definition in cls._definitions.values()]

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
