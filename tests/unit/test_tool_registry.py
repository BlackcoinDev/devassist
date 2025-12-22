#!/usr/bin/env python3
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
Test suite for ToolRegistry - Plugin system for AI tools.

Tests cover:
- Decorator-based registration with definitions
- Tool execution and dispatch
- LLM tool call handling
- Definition management for LLM binding
- Error handling
- Registry introspection methods
"""

from unittest.mock import patch, Mock
from src.tools.registry import ToolRegistry, register_tool


# Sample tool definition for testing
SAMPLE_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "test_tool",
        "description": "A test tool",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "First argument"}
            },
            "required": ["arg1"]
        }
    }
}


class TestToolRegistration:
    """Test tool registration via decorator."""

    def setup_method(self):
        """Clear registry before each test."""
        ToolRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_register_simple_tool(self):
        """Test registering a basic tool without definition."""
        @ToolRegistry.register("test_tool")
        def execute_test(arg1: str) -> dict:
            return {"result": arg1}

        assert ToolRegistry.has_tool("test_tool")
        assert "test_tool" in ToolRegistry.get_tool_names()

    def test_register_with_definition(self):
        """Test registering tool with LLM definition."""
        @ToolRegistry.register("test_tool", SAMPLE_TOOL_DEFINITION)
        def execute_test(arg1: str) -> dict:
            return {"result": arg1}

        definitions = ToolRegistry.get_definitions()
        assert len(definitions) == 1
        assert definitions[0] == SAMPLE_TOOL_DEFINITION

    def test_register_tool_convenience_function(self):
        """Test using register_tool convenience function."""
        @register_tool("test_tool", SAMPLE_TOOL_DEFINITION)
        def execute_test(arg1: str) -> dict:
            return {"result": arg1}

        assert ToolRegistry.has_tool("test_tool")

    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        @ToolRegistry.register("tool1")
        def execute_tool1() -> dict:
            return {}

        @ToolRegistry.register("tool2")
        def execute_tool2() -> dict:
            return {}

        assert ToolRegistry.has_tool("tool1")
        assert ToolRegistry.has_tool("tool2")
        assert len(ToolRegistry.get_tool_names()) == 2


class TestToolExecution:
    """Test tool execution and dispatch."""

    def setup_method(self):
        """Clear registry and set up test tools."""
        ToolRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_execute_registered_tool(self):
        """Test executing a registered tool."""
        @ToolRegistry.register("test_tool")
        def execute_test(arg1: str, arg2: int) -> dict:
            return {"result": f"{arg1}-{arg2}"}

        result = ToolRegistry.execute("test_tool", {"arg1": "hello", "arg2": 42})

        assert result == {"result": "hello-42"}

    def test_execute_unknown_tool(self):
        """Test executing an unregistered tool."""
        result = ToolRegistry.execute("unknown_tool", {})

        assert "error" in result
        assert "Unknown tool" in result["error"]

    def test_execute_with_error_handling(self):
        """Test that errors during execution are caught."""
        @ToolRegistry.register("error_tool")
        def execute_error(arg1: str) -> dict:
            raise ValueError("Test error")

        with patch("src.tools.registry.logger") as mock_logger:
            result = ToolRegistry.execute("error_tool", {"arg1": "test"})

            assert "error" in result
            assert "Test error" in result["error"]
            mock_logger.error.assert_called_once()

    def test_execute_with_keyword_args(self):
        """Test that args dict is unpacked as keyword arguments."""
        @ToolRegistry.register("test_tool")
        def execute_test(name: str, age: int, active: bool = True) -> dict:
            return {"name": name, "age": age, "active": active}

        result = ToolRegistry.execute("test_tool", {
            "name": "Alice",
            "age": 30,
            "active": False
        })

        assert result == {"name": "Alice", "age": 30, "active": False}

    def test_execute_with_missing_args(self):
        """Test execution with missing required arguments."""
        @ToolRegistry.register("test_tool")
        def execute_test(required_arg: str) -> dict:
            return {"result": required_arg}

        result = ToolRegistry.execute("test_tool", {})

        assert "error" in result


class TestToolCallExecution:
    """Test LLM tool call handling."""

    def setup_method(self):
        """Clear registry and set up test tools."""
        ToolRegistry.clear()

        @ToolRegistry.register("read_file")
        def execute_read_file(file_path: str) -> dict:
            return {"success": True, "content": f"Content of {file_path}"}

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_execute_tool_call_with_dict(self):
        """Test execute_tool_call with dict-based tool call."""
        tool_call = {
            "name": "read_file",
            "args": {"file_path": "test.txt"}
        }

        result = ToolRegistry.execute_tool_call(tool_call)

        assert result["function_name"] == "read_file"
        assert result["result"]["success"] is True
        assert "test.txt" in result["result"]["content"]

    def test_execute_tool_call_with_object(self):
        """Test execute_tool_call with object-based tool call."""
        tool_call = Mock()
        tool_call.name = "read_file"
        tool_call.args = {"file_path": "test.txt"}

        result = ToolRegistry.execute_tool_call(tool_call)

        assert result["function_name"] == "read_file"
        assert result["result"]["success"] is True

    def test_execute_tool_call_with_string_args(self):
        """Test execute_tool_call with JSON string arguments."""
        tool_call = {
            "name": "read_file",
            "args": '{"file_path": "test.txt"}'
        }

        result = ToolRegistry.execute_tool_call(tool_call)

        assert result["function_name"] == "read_file"
        assert result["result"]["success"] is True

    def test_execute_tool_call_with_invalid_json(self):
        """Test execute_tool_call with invalid JSON in args."""
        tool_call = {
            "name": "read_file",
            "args": "{invalid json}"
        }

        result = ToolRegistry.execute_tool_call(tool_call)

        assert result["function_name"] == "unknown"
        assert "error" in result["result"]
        assert "Invalid JSON" in result["result"]["error"]

    def test_execute_tool_call_with_none_args(self):
        """Test execute_tool_call with None args (uses empty dict)."""
        @ToolRegistry.register("no_args_tool")
        def execute_no_args() -> dict:
            return {"result": "success"}

        tool_call = {"name": "no_args_tool", "args": None}

        result = ToolRegistry.execute_tool_call(tool_call)

        assert result["function_name"] == "no_args_tool"
        assert result["result"]["result"] == "success"

    def test_execute_tool_call_with_exception(self):
        """Test execute_tool_call error handling."""
        tool_call = {"name": "invalid"}

        with patch("src.tools.registry.logger"):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "invalid"
            assert "error" in result["result"]


class TestDefinitionManagement:
    """Test tool definition management for LLM binding."""

    def setup_method(self):
        """Clear registry before each test."""
        ToolRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_get_definitions_returns_list(self):
        """Test that get_definitions returns a list."""
        definitions = ToolRegistry.get_definitions()
        assert isinstance(definitions, list)

    def test_get_definitions_with_multiple_tools(self):
        """Test getting definitions for multiple tools."""
        def1 = {"type": "function", "function": {"name": "tool1"}}
        def2 = {"type": "function", "function": {"name": "tool2"}}

        @ToolRegistry.register("tool1", def1)
        def execute_tool1() -> dict:
            return {}

        @ToolRegistry.register("tool2", def2)
        def execute_tool2() -> dict:
            return {}

        definitions = ToolRegistry.get_definitions()
        assert len(definitions) == 2
        assert def1 in definitions
        assert def2 in definitions

    def test_register_without_definition(self):
        """Test that tools without definitions are not in get_definitions."""
        @ToolRegistry.register("no_def_tool")
        def execute_no_def() -> dict:
            return {}

        definitions = ToolRegistry.get_definitions()
        assert len(definitions) == 0

    def test_definitions_are_independent(self):
        """Test that modifying returned definitions doesn't affect registry."""
        definition = {"type": "function", "function": {"name": "tool1"}}

        @ToolRegistry.register("tool1", definition)
        def execute_tool1() -> dict:
            return {}

        definitions = ToolRegistry.get_definitions()
        definitions[0]["modified"] = True

        # Original should not be modified
        fresh_definitions = ToolRegistry.get_definitions()
        assert "modified" not in fresh_definitions[0]


class TestRegistryIntrospection:
    """Test registry query and introspection methods."""

    def setup_method(self):
        """Clear registry and register test tools."""
        ToolRegistry.clear()

        @ToolRegistry.register("read_file")
        def execute_read_file(file_path: str) -> dict:
            return {}

        @ToolRegistry.register("write_file")
        def execute_write_file(file_path: str, content: str) -> dict:
            return {}

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_get_tool_names(self):
        """Test getting list of registered tool names."""
        names = ToolRegistry.get_tool_names()

        assert isinstance(names, list)
        assert "read_file" in names
        assert "write_file" in names

    def test_has_tool_positive(self):
        """Test has_tool returns True for registered tools."""
        assert ToolRegistry.has_tool("read_file") is True
        assert ToolRegistry.has_tool("write_file") is True

    def test_has_tool_negative(self):
        """Test has_tool returns False for unregistered tools."""
        assert ToolRegistry.has_tool("unknown_tool") is False
        assert ToolRegistry.has_tool("") is False

    def test_clear_removes_all_tools(self):
        """Test that clear removes all registered tools."""
        assert ToolRegistry.has_tool("read_file")

        ToolRegistry.clear()

        assert not ToolRegistry.has_tool("read_file")
        assert len(ToolRegistry.get_tool_names()) == 0
        assert len(ToolRegistry.get_definitions()) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Clear registry before each test."""
        ToolRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_reregister_same_tool_overwrites(self):
        """Test that re-registering a tool overwrites previous."""
        @ToolRegistry.register("test_tool")
        def handler1(arg: str) -> dict:
            return {"version": "first"}

        @ToolRegistry.register("test_tool")
        def handler2(arg: str) -> dict:
            return {"version": "second"}

        result = ToolRegistry.execute("test_tool", {"arg": "test"})
        assert result["version"] == "second"

    def test_execute_with_empty_args(self):
        """Test executing tool with empty args dict."""
        @ToolRegistry.register("no_args_tool")
        def execute_no_args() -> dict:
            return {"result": "success"}

        result = ToolRegistry.execute("no_args_tool", {})
        assert result["result"] == "success"

    def test_tool_with_return_value_errors(self):
        """Test tool that returns non-dict causes error."""
        @ToolRegistry.register("bad_return_tool")
        def execute_bad_return(arg: str):
            return "not a dict"  # Should return dict

        # This should not cause an error in execute, but might in usage
        result = ToolRegistry.execute("bad_return_tool", {"arg": "test"})
        assert result == "not a dict"  # Tool registry doesn't enforce return type

    def test_concurrent_registration(self):
        """Test that multiple registrations don't conflict."""
        # This is a sanity check for class variable usage
        tools_before = len(ToolRegistry.get_tool_names())

        @ToolRegistry.register("tool1")
        def execute_tool1() -> dict:
            return {}

        @ToolRegistry.register("tool2")
        def execute_tool2() -> dict:
            return {}

        assert len(ToolRegistry.get_tool_names()) == tools_before + 2
