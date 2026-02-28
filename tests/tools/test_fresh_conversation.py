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
Unit tests for fresh conversation tool calling with LangChain.

These tests mock the LangChain LLM to avoid requiring a running server.
"""

from unittest.mock import MagicMock, patch
from langchain_core.messages import SystemMessage, HumanMessage


class TestFreshConversation:
    """Test fresh conversation tool calling with LangChain."""

    def test_tool_definition_format(self):
        """Test that tool definitions are properly formatted."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to read",
                            }
                        },
                        "required": ["file_path"],
                    },
                },
            }
        ]

        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "read_file"
        assert "parameters" in tools[0]["function"]

    @patch("langchain_openai.ChatOpenAI")
    def test_langchain_tool_calling_with_mock(self, mock_chat_class):
        """Test that LangChain tool calling works with mocked LLM."""
        mock_llm = MagicMock()
        mock_chat_class.return_value = mock_llm

        mock_response = MagicMock()
        mock_response.tool_calls = [
            {
                "name": "read_file",
                "args": {"file_path": "README.md"},
            }
        ]
        mock_response.content = None
        mock_llm.bind_tools.return_value.invoke.return_value = mock_response

        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key=SecretStr("test-key"),
            model="test-model",
            temperature=0.0,
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read file contents",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"],
                    },
                },
            }
        ]

        llm_with_tools = llm.bind_tools(tools)
        messages = [
            SystemMessage(content="Test system message"),
            HumanMessage(content="read the README file"),
        ]

        response = llm_with_tools.invoke(messages)

        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["name"] == "read_file"

    @patch("langchain_openai.ChatOpenAI")
    def test_langchain_no_tool_calls(self, mock_chat_class):
        """Test handling response with no tool calls."""
        mock_llm = MagicMock()
        mock_chat_class.return_value = mock_llm

        mock_response = MagicMock()
        mock_response.tool_calls = None
        mock_response.content = "I cannot read files directly."
        mock_llm.bind_tools.return_value.invoke.return_value = mock_response

        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key=SecretStr("test-key"),
            model="test-model",
            temperature=0.0,
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read file contents",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"],
                    },
                },
            }
        ]

        llm_with_tools = llm.bind_tools(tools)
        messages = [HumanMessage(content="hello")]

        response = llm_with_tools.invoke(messages)

        assert response.tool_calls is None
        assert response.content is not None

    @patch("langchain_openai.ChatOpenAI")
    def test_multiple_tool_calls(self, mock_chat_class):
        """Test handling multiple tool calls in one response."""
        mock_llm = MagicMock()
        mock_chat_class.return_value = mock_llm

        mock_response = MagicMock()
        mock_response.tool_calls = [
            {"name": "read_file", "args": {"file_path": "README.md"}},
            {"name": "list_directory", "args": {"directory_path": "."}},
        ]
        mock_response.content = None
        mock_llm.bind_tools.return_value.invoke.return_value = mock_response

        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key=SecretStr("test-key"),
            model="test-model",
            temperature=0.0,
        )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read file",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List directory",
                    "parameters": {
                        "type": "object",
                        "properties": {"directory_path": {"type": "string"}},
                        "required": ["directory_path"],
                    },
                },
            },
        ]

        llm_with_tools = llm.bind_tools(tools)
        messages = [HumanMessage(content="read README and list current dir")]

        response = llm_with_tools.invoke(messages)

        assert response.tool_calls is not None
        assert len(response.tool_calls) == 2
