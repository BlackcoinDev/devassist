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
Unit tests for Export Commands.

Tests cover:
- JSON export format
- Markdown export format
- Empty conversation handling
- Invalid format handling
- File creation verification
"""

import unittest
import tempfile
import os
import json
from io import StringIO
import sys
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.commands.handlers.export_commands import handle_export


class TestHandleExportEmpty(unittest.TestCase):
    """Test export with empty conversation."""

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_no_history(self, mock_get_ctx):
        """Test export when no conversation history exists."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = []
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export([])
        sys.stdout = sys.__stdout__

        self.assertIn("No conversation history", captured.getvalue())


class TestHandleExportJSON(unittest.TestCase):
    """Test JSON export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_json_default(self, mock_get_ctx):
        """Test default JSON export."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export([])  # Default is JSON
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("exported to", output)
        self.assertIn("JSON", output)

        # Find the exported file
        json_files = [f for f in os.listdir(self.tmpdir.name) if f.endswith(".json")]
        self.assertEqual(len(json_files), 1)

        # Verify JSON content
        with open(os.path.join(self.tmpdir.name, json_files[0]), "r") as f:
            data = json.load(f)

        self.assertIn("messages", data)
        self.assertEqual(len(data["messages"]), 2)
        self.assertEqual(data["messages"][0]["content"], "Hello")
        self.assertEqual(data["messages"][1]["content"], "Hi there!")

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_json_explicit(self, mock_get_ctx):
        """Test explicit JSON export."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="Test message"),
        ]
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export(["json"])
        sys.stdout = sys.__stdout__

        self.assertIn("JSON", captured.getvalue())

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_json_message_types(self, mock_get_ctx):
        """Test JSON export with different message types."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            SystemMessage(content="System prompt"),
            HumanMessage(content="User message"),
            AIMessage(content="AI response"),
        ]
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export(["json"])
        sys.stdout = sys.__stdout__

        # Find and read exported file
        json_files = [f for f in os.listdir(self.tmpdir.name) if f.endswith(".json")]
        with open(os.path.join(self.tmpdir.name, json_files[0]), "r") as f:
            data = json.load(f)

        # Verify message types
        types = [m["type"] for m in data["messages"]]
        self.assertIn("system", types)
        self.assertIn("human", types)
        self.assertIn("ai", types)


class TestHandleExportMarkdown(unittest.TestCase):
    """Test Markdown export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_markdown(self, mock_get_ctx):
        """Test Markdown export."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export(["markdown"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("exported to", output)
        self.assertIn("MARKDOWN", output)

        # Find the exported file
        md_files = [f for f in os.listdir(self.tmpdir.name) if f.endswith(".md")]
        self.assertEqual(len(md_files), 1)

        # Verify Markdown content
        with open(os.path.join(self.tmpdir.name, md_files[0]), "r") as f:
            content = f.read()

        self.assertIn("# Conversation Export", content)
        self.assertIn("Hello", content)
        self.assertIn("Hi there!", content)

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_md_shorthand(self, mock_get_ctx):
        """Test 'md' shorthand for markdown export."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="Test"),
        ]
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export(["md"])
        sys.stdout = sys.__stdout__

        # Should export as markdown
        md_files = [f for f in os.listdir(self.tmpdir.name) if f.endswith(".md")]
        self.assertEqual(len(md_files), 1)


class TestHandleExportInvalidFormat(unittest.TestCase):
    """Test invalid export format handling."""

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_invalid_format(self, mock_get_ctx):
        """Test export with invalid format."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="Test"),
        ]
        mock_get_ctx.return_value = mock_ctx

        captured = StringIO()
        sys.stdout = captured
        handle_export(["xml"])  # Invalid format
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Unsupported format", output)
        self.assertIn("xml", output)


class TestHandleExportMetadata(unittest.TestCase):
    """Test export metadata and formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_includes_timestamp(self, mock_get_ctx):
        """Test that export includes timestamp metadata."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="Hello"),
        ]
        mock_get_ctx.return_value = mock_ctx

        handle_export(["json"])

        # Find and read exported file
        json_files = [f for f in os.listdir(self.tmpdir.name) if f.endswith(".json")]
        with open(os.path.join(self.tmpdir.name, json_files[0]), "r") as f:
            data = json.load(f)

        self.assertIn("export_timestamp", data)
        self.assertIn("total_messages", data)
        self.assertEqual(data["total_messages"], 1)

    @patch("src.commands.handlers.export_commands.get_context")
    def test_export_message_index(self, mock_get_ctx):
        """Test that messages have correct indices."""
        mock_ctx = MagicMock()
        mock_ctx.conversation_history = [
            HumanMessage(content="First"),
            AIMessage(content="Second"),
            HumanMessage(content="Third"),
        ]
        mock_get_ctx.return_value = mock_ctx

        handle_export(["json"])

        json_files = [f for f in os.listdir(self.tmpdir.name) if f.endswith(".json")]
        with open(os.path.join(self.tmpdir.name, json_files[0]), "r") as f:
            data = json.load(f)

        indices = [m["index"] for m in data["messages"]]
        self.assertEqual(indices, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
