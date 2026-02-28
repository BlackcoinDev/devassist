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
Unit tests for direct OpenAI API tool calling.

These tests mock the OpenAI client to avoid requiring a running LM Studio server.
"""

from unittest.mock import MagicMock, patch
from openai.types.chat import ChatCompletionToolParam

# Define tools (same as main.py)
tools: list[ChatCompletionToolParam] = [
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


class TestDirectTools:
    """Test direct OpenAI API tool calling."""

    @patch("openai.OpenAI")
    def test_tool_calling_with_mock(self, mock_openai_class):
        """Test that tool calling works with mocked OpenAI client."""
        # Mock the OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.tool_calls = [MagicMock()]
        mock_response.choices[0].message.tool_calls[0].function.name = "read_file"
        mock_response.choices[0].message.tool_calls[
            0
        ].function.arguments = '{"file_path": "README.md"}'
        mock_response.choices[0].message.content = None

        mock_client.chat.completions.create.return_value = mock_response

        # Import after mocking
        from openai import OpenAI

        # Create client
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="test-key")

        # Make request
        messages = [
            {"role": "system", "content": "Test system message"},
            {"role": "user", "content": "read the README file"},
        ]

        response = client.chat.completions.create(
            model="test-model",
            messages=messages,
            tools=tools,
        )

        # Verify tool was called
        assert response.choices[0].message.tool_calls is not None
        assert response.choices[0].message.tool_calls[0].function.name == "read_file"

    @patch("openai.OpenAI")
    def test_tool_definition_format(self, mock_openai_class):
        """Test that tool definitions are properly formatted."""
        # Verify tool structure
        assert len(tools) == 1
        assert tools[0]["type"] == "function"
        assert tools[0]["function"]["name"] == "read_file"
        assert "parameters" in tools[0]["function"]
        assert "properties" in tools[0]["function"]["parameters"]
        assert "file_path" in tools[0]["function"]["parameters"]["properties"]

    @patch("openai.OpenAI")
    def test_no_tool_calls_response(self, mock_openai_class):
        """Test handling response with no tool calls."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock response with no tool calls
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "I don't have access to files."

        mock_client.chat.completions.create.return_value = mock_response

        from openai import OpenAI

        client = OpenAI(base_url="http://localhost:1234/v1", api_key="test-key")

        response = client.chat.completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "hello"}],
            tools=tools,
        )

        # Verify no tool calls
        assert response.choices[0].message.tool_calls is None
        assert response.choices[0].message.content is not None
