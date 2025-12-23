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

"""End-to-end tests for the AI Assistant application."""

import unittest
from unittest.mock import patch

from src.main import main


class TestEndToEnd(unittest.TestCase):
    """Test end-to-end application flows."""

    @patch("src.main.initialize_application")
    @patch("src.main.ChatLoop")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_basic_session_flow(self, mock_print, mock_input, mock_chat_loop, mock_init):
        """Test application initialization and basic functionality."""
        # 1. Setup mocks for current architecture
        mock_init.return_value = True
        mock_input.side_effect = ["Hi", "exit"]
        mock_chat_loop.return_value.run_iteration.return_value = "Mock response"

        # 2. Test that main() runs without errors
        result = main()

        # 3. Verify basic application behavior
        # The main function should initialize and run without crashing
        assert result is True  # main() returns True on successful initialization
        mock_init.assert_called_once()  # initialize_application should be called

    @patch("src.main.initialize_application")
    @patch("src.main.handle_slash_command")
    @patch("builtins.input")
    def test_slash_command_flow(self, mock_input, mock_slash, mock_init):
        """Test application responds to initialization request."""
        mock_init.return_value = True
        mock_input.side_effect = ["/help", "exit"]

        # Test that main() runs without errors
        result = main()

        # Verify basic functionality
        assert result is True
        mock_init.assert_called_once()
        mock_slash.assert_called_once()

    @patch("src.main.initialize_application")
    @patch("builtins.input")
    def test_empty_input_handling(self, mock_input, mock_init):
        """Test application handles empty input gracefully."""
        mock_init.return_value = True
        mock_input.side_effect = ["", "exit"]

        # Test that main() runs without errors even with empty input
        result = main()

        # Verify basic functionality
        assert result is True
        mock_init.assert_called_once()


if __name__ == "__main__":
    unittest.main()
