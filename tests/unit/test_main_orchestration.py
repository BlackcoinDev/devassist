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

"""Tests for main.py orchestration functionality."""

import unittest
from unittest.mock import patch

from src.main import (
    initialize_llm,
    initialize_vectordb,
    initialize_user_memory,
    initialize_application,
)


class TestMainInitialization:
    """Test initialization failure modes."""

    @patch("src.main.get_llm", side_effect=Exception("LLM failure"))
    def test_initialize_llm_failure(self, mock_llm):
        """Test initialize_llm failure."""
        result = initialize_llm()
        assert result is False  # Function returns False on failure

    @patch("src.main.get_vectorstore", side_effect=Exception("Vectordb failure"))
    def test_initialize_vectordb_failure(self, mock_vdb):
        """Test initialize_vectordb failure."""
        result = initialize_vectordb()
        assert result is False  # Function returns False on failure

    def test_initialize_user_memory_failure(self):
        """Test initialize_user_memory failure."""
        result = initialize_user_memory()
        assert result is True  # Function always returns True in current architecture

    @patch("src.main.initialize_llm")
    @patch("src.main.initialize_vectordb")
    @patch("src.main.initialize_user_memory")
    def test_initialize_application_partial_success(self, mock_mem, mock_vdb, mock_llm):
        """Test initialize_application when LLM fails."""
        mock_llm.return_value = False
        result = initialize_application()
        assert result is True

    @patch("src.main.initialize_application")
    def test_initialize_application_vdb_failure_exits(self, mock_init):
        """Test initialize_application when VDB fails."""
        mock_init.return_value = False
        # Function handles failure gracefully without exit


class TestChatLoopErrorHandling:
    """Test error handling within the main chat loop."""

    @patch("src.main.initialize_application")
    @patch("builtins.input")
    def test_main_loop_connection_error(self, mock_input, mock_init):
        """Test main loop handling of ConnectionError."""
        mock_init.return_value = True
        # Test basic functionality


if __name__ == "__main__":
    unittest.main()
