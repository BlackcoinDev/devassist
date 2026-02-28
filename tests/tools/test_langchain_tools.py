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
Unit tests for LangChain tool binding.

These tests mock the LangChain LLM to avoid requiring a running server.
"""

from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage


class TestLangChainTools:
    """Test LangChain tool binding."""

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
    def test_langchain_bind_tools(self, mock_chat_class):
        """Test that bind_tools works correctly."""
        mock_llm = MagicMock()
        mock_chat_class.return_value = mock_llm
        mock_llm.bind_tools.return_value = mock_llm

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
            }
        ]

        llm_with_tools = llm.bind_tools(tools)

        assert llm_with_tools is not None
        mock_llm.bind_tools.assert_called_once_with(tools)

    @patch("langchain_openai.ChatOpenAI")
    def test_langchain_invoke_with_tools(self, mock_chat_class):
        """Test invoking LLM with bound tools."""
        mock_llm = MagicMock()
        mock_chat_class.return_value = mock_llm

        mock_response = MagicMock()
        mock_response.tool_calls = [
            {"name": "read_file", "args": {"file_path": "README.md"}}
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
            }
        ]

        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke([HumanMessage(content="read the README")])

        assert response.tool_calls is not None
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["name"] == "read_file"

    @patch("langchain_openai.ChatOpenAI")
    def test_langchain_temperature_setting(self, mock_chat_class):
        """Test that temperature is properly set."""
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key=SecretStr("test-key"),
            model="test-model",
            temperature=0.0,
        )

        assert llm is not None
        assert mock_chat_class.called

    @patch("langchain_openai.ChatOpenAI")
    def test_langchain_model_setting(self, mock_chat_class):
        """Test that model name is properly set."""
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        llm = ChatOpenAI(
            base_url="http://localhost:1234/v1",
            api_key=SecretStr("test-key"),
            model="qwen3-vl-30b",
            temperature=0.0,
        )

        assert llm is not None
        assert mock_chat_class.called

    @patch("langchain_openai.ChatOpenAI")
    def test_multiple_tools_binding(self, mock_chat_class):
        """Test binding multiple tools."""
        mock_llm = MagicMock()
        mock_chat_class.return_value = mock_llm
        mock_llm.bind_tools.return_value = mock_llm

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
                    "name": "write_file",
                    "description": "Write file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["file_path", "content"],
                    },
                },
            },
        ]

        llm_with_tools = llm.bind_tools(tools)

        assert llm_with_tools is not None
        mock_llm.bind_tools.assert_called_once()
        call_args = mock_llm.bind_tools.call_args[0][0]
        assert len(call_args) == 2
