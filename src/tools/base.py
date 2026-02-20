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

"""Async tool support for DevAssist.

This module provides infrastructure for async tool execution, allowing
tools to run asynchronously while maintaining backward compatibility
with synchronous tools.
"""

import asyncio
import inspect
from typing import Dict, Any, Callable, Union

# Registry of async tools
_async_tools: Dict[str, Callable] = {}


def is_async_tool(name: str) -> bool:
    """Check if a tool is registered as async.

    Args:
        name: Tool name

    Returns:
        bool: True if tool is async
    """
    return name in _async_tools


def register_async_tool(name: str, func: Callable) -> None:
    """Register a tool as async-capable.

    Args:
        name: Tool name
        func: Async function to register
    """
    _async_tools[name] = func


def get_async_tool(name: str) -> Union[Callable, None]:
    """Get an async tool by name.

    Args:
        name: Tool name

    Returns:
        Async function or None if not found
    """
    return _async_tools.get(name)


def is_async_function(func: Callable) -> bool:
    """Check if a function is async (coroutine).

    Args:
        func: Function to check

    Returns:
        bool: True if function is async
    """
    return asyncio.iscoroutinefunction(func)


async def run_tool_async(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a tool asynchronously.

    Args:
        name: Tool name
        args: Tool arguments

    Returns:
        Tool result dictionary
    """
    tool = get_async_tool(name)
    if tool is None:
        return {"error": f"Async tool '{name}' not found"}

    try:
        result = await tool(**args)
        return result if isinstance(result, dict) else {"result": result}
    except Exception as e:
        return {"error": str(e)}


class AsyncToolMixin:
    """Mixin class for tools that support async execution.

    Tools inheriting from this mixin can provide both sync and async
    execution methods. The async method should be named with _async suffix.
    """

    async def execute_async(self, **kwargs) -> Dict[str, Any]:
        """Execute tool asynchronously.

        Override this method in subclasses for async execution.

        Returns:
            Tool result dictionary
        """
        raise NotImplementedError("Subclasses must implement execute_async")


__all__ = [
    "is_async_tool",
    "register_async_tool",
    "get_async_tool",
    "is_async_function",
    "run_tool_async",
    "AsyncToolMixin",
]
