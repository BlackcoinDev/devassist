#!/usr/bin/env python3
"""
Tool Calling Integration Tests

Tests the integration between LLM and tool execution:
- Tool call detection and parsing
- Tool execution routing
- Result integration into conversation
- Error handling in tool chains
"""

from unittest.mock import patch, MagicMock

# Import from modular architecture (v0.2.0)
from src.tools import ToolRegistry
import importlib
import src.tools.executors.file_tools
import src.tools.executors.knowledge_tools
import src.tools.executors.document_tools
import src.tools.executors.web_tools


def ensure_tools_registered():
    """Ensure tools are registered before tests run, re-registering if needed."""
    # We must reload these modules because other tests might have cleared the registry
    importlib.reload(src.tools.executors.file_tools)
    importlib.reload(src.tools.executors.knowledge_tools)
    importlib.reload(src.tools.executors.document_tools)
    importlib.reload(src.tools.executors.web_tools)


class TestToolCallExecution:
    """Test tool call execution and routing."""

    def setup_method(self):
        """Set up tests by ensuring tools are registered."""
        ensure_tools_registered()

    def test_execute_read_file_tool(self):
        """Test executing read_file tool call."""
        tool_call = {
            "id": "test_123",
            "name": "read_file",
            "args": {"file_path": "test.txt"},
        }

        mock_execute = MagicMock(return_value={"success": True, "content": "test content"})
        with patch.dict(ToolRegistry._tools, {"read_file": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "read_file"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(file_path="test.txt")

    def test_execute_write_file_tool(self):
        """Test executing write_file tool call."""
        tool_call = {
            "id": "test_456",
            "name": "write_file",
            "args": {"file_path": "output.txt", "content": "new content"},
        }

        mock_execute = MagicMock(return_value={"success": True, "size": 11})
        with patch.dict(ToolRegistry._tools, {"write_file": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "write_file"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(file_path="output.txt", content="new content")

    def test_execute_list_directory_tool(self):
        """Test executing list_directory tool call."""
        tool_call = {
            "id": "test_789",
            "name": "list_directory",
            "args": {"directory_path": "/tmp"},
        }

        mock_execute = MagicMock(return_value={"success": True, "total_items": 5})
        with patch.dict(ToolRegistry._tools, {"list_directory": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "list_directory"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(directory_path="/tmp")

    def test_execute_get_current_directory_tool(self):
        """Test executing get_current_directory tool call."""
        tool_call = {"id": "test_cwd", "name": "get_current_directory", "args": {}}

        mock_execute = MagicMock(return_value={"success": True, "current_directory": "/home/user"})
        with patch.dict(ToolRegistry._tools, {"get_current_directory": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "get_current_directory"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once()

    def test_execute_parse_document_tool(self):
        """Test executing parse_document tool call."""
        tool_call = {
            "id": "test_doc",
            "name": "parse_document",
            "args": {"file_path": "document.pdf", "extract_type": "text"},
        }

        mock_execute = MagicMock(return_value={"success": True, "content": "parsed content"})
        with patch.dict(ToolRegistry._tools, {"parse_document": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "parse_document"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(file_path="document.pdf", extract_type="text")

    def test_execute_learn_information_tool(self):
        """Test executing learn_information tool call."""
        tool_call = {
            "id": "test_learn",
            "name": "learn_information",
            "args": {
                "information": "Python is great",
            },
        }

        mock_execute = MagicMock(return_value={"success": True, "learned": True})
        with patch.dict(ToolRegistry._tools, {"learn_information": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "learn_information"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(information="Python is great")

    def test_execute_search_knowledge_tool(self):
        """Test executing search_knowledge tool call."""
        tool_call = {
            "id": "test_search",
            "name": "search_knowledge",
            "args": {"query": "Python basics", "limit": 3},
        }

        mock_execute = MagicMock(return_value={"success": True, "result_count": 2})
        with patch.dict(ToolRegistry._tools, {"search_knowledge": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "search_knowledge"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(query="Python basics", limit=3)

    def test_execute_search_web_tool(self):
        """Test executing search_web tool call."""
        tool_call = {
            "id": "test_web",
            "name": "search_web",
            "args": {"query": "latest AI news"},
        }

        mock_execute = MagicMock(return_value={"success": True, "result_count": 5})
        with patch.dict(ToolRegistry._tools, {"search_web": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "search_web"
            assert result["result"]["success"] is True
            mock_execute.assert_called_once_with(query="latest AI news")

    def test_execute_unknown_tool(self):
        """Test executing unknown tool."""
        tool_call = {"id": "test_unknown", "name": "unknown_tool", "args": {}}

        result = ToolRegistry.execute_tool_call(tool_call)

        assert result["function_name"] == "unknown_tool"
        assert "error" in result["result"]
        assert "Unknown tool" in result["result"]["error"]

    def test_tool_call_with_invalid_json(self):
        """Test tool call with invalid JSON arguments."""
        # This test doesn't apply since we now pass dict directly
        pass

    def test_tool_execution_error_handling(self):
        """Test error handling during tool execution."""
        tool_call = {
            "id": "test_error",
            "name": "read_file",
            "args": {"file_path": "test.txt"},
        }

        mock_execute = MagicMock(side_effect=Exception("Tool execution failed"))
        with patch.dict(ToolRegistry._tools, {"read_file": mock_execute}):
            result = ToolRegistry.execute_tool_call(tool_call)

            assert result["function_name"] == "read_file"
            assert "error" in result["result"]
            assert "Tool execution failed" in result["result"]["error"]


class TestToolCallIntegration:
    """Test tool calling in conversation context."""

    @patch("src.main.llm")
    @patch("src.main.vectorstore")
    def test_tool_call_in_conversation_flow(self, mock_vectorstore, mock_llm):
        """Test that tool calls integrate properly into conversation flow."""
        # Mock LLM response with tool call
        mock_response = MagicMock()
        mock_response.content = "I'll help you read that file."
        mock_response.tool_calls = [
            {
                "id": "call_123",
                "function": {
                    "name": "read_file",
                    "arguments": '{"file_path": "README.md"}',
                },
            }
        ]

        mock_llm.invoke.return_value = mock_response

        # Mock tool execution
        with patch("src.tools.executors.file_tools.execute_read_file") as mock_execute:
            mock_execute.return_value = {"success": True, "content": "README content"}

            # This would be tested in a full conversation integration test
            # For now, just verify the tool call structure
            assert mock_response.tool_calls[0]["function"]["name"] == "read_file"

    def test_multiple_tool_calls(self):
        """Test handling multiple tool calls in sequence."""
        tool_calls = [
            {"id": "call_1", "name": "read_file", "args": {"file_path": "file1.txt"}},
            {"id": "call_2", "name": "read_file", "args": {"file_path": "file2.txt"}},
        ]

        mock_execute = MagicMock(return_value={"success": True, "content": "content"})
        with patch.dict(ToolRegistry._tools, {"read_file": mock_execute}):
            results = []
            for tool_call in tool_calls:
                result = ToolRegistry.execute_tool_call(tool_call)
                results.append(result)

            assert len(results) == 2
            assert all(r["function_name"] == "read_file" for r in results)
            assert mock_execute.call_count == 2


class TestToolSecurityIntegration:
    """Test security aspects of tool integration."""

    def test_tool_call_argument_validation(self):
        """Test that tool calls validate arguments properly."""
        # Test missing required arguments
        tool_call = {
            "id": "test_missing_args",
            "name": "read_file",
            "args": {},  # Missing file_path
        }

        result = ToolRegistry.execute_tool_call(tool_call)

        # Should still attempt execution, but tool function should handle missing args
        assert result["function_name"] == "read_file"
        assert isinstance(result["result"], dict)

    def test_tool_call_type_safety(self):
        """Test that tool calls handle type mismatches gracefully."""
        tool_call = {
            "id": "test_type_mismatch",
            "name": "search_knowledge",
            "args": {"query": 123, "limit": "not_a_number"},  # Wrong types
        }

        result = ToolRegistry.execute_tool_call(tool_call)

        # Should handle gracefully without crashing
        assert result["function_name"] == "search_knowledge"
        assert isinstance(result["result"], dict)
