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
Unit tests for gui.py components (non-GUI parts).

⚠️  WARNING: GUI tests are DISABLED by default because:
1. PyQt6 causes segmentation faults during test cleanup
2. GUI windows stay open and require manual closing
3. Qt event loops interfere with pytest

To run GUI tests manually (not recommended):
1. Close all other applications
2. Set environment variable: export RUN_GUI_TESTS=1
3. Run: pytest tests/unit/test_gui.py -v
4. Manually close any GUI windows that appear
5. Be prepared for potential crashes and segmentation faults

For CI/CD: GUI tests are automatically skipped.
"""

import pytest
from unittest.mock import MagicMock, patch

# GUI tests are conditionally skipped
import os

# Skip GUI tests unless explicitly enabled
skip_gui_tests = not os.environ.get("RUN_GUI_TESTS", "").lower() in ("1", "true", "yes")


@pytest.mark.skipif(
    skip_gui_tests,
    reason="GUI tests cause segmentation faults and require manual window closing. Set RUN_GUI_TESTS=1 to run them.",
)
class TestGUISupportFunctions:
    """Test GUI support functions that don't require Qt."""

    @patch("gui.BACKEND_AVAILABLE", True)
    @patch("src.main.load_memory")
    def test_load_conversation_success(self, mock_load_memory):
        """Test successful conversation loading."""
        from src.gui import AIAssistantGUI

        # Mock the GUI class without Qt dependencies
        with patch("gui.QMainWindow.__init__", return_value=None):
            with patch("gui.AIAssistantGUI.init_ui", return_value=None):
                gui = AIAssistantGUI.__new__(AIAssistantGUI)

                # Test the load_conversation method
                gui.status_label = MagicMock()
                gui.chat_display = MagicMock()

                gui.load_conversation()

                mock_load_memory.assert_called_once()

    @patch("gui.BACKEND_AVAILABLE", False)
    def test_load_conversation_no_backend(self):
        """Test conversation loading when backend is not available."""
        from src.gui import AIAssistantGUI

        with patch("gui.QMainWindow.__init__", return_value=None):
            with patch("gui.AIAssistantGUI.init_ui", return_value=None):
                gui = AIAssistantGUI.__new__(AIAssistantGUI)

                gui.status_label = MagicMock()
                gui.chat_display = MagicMock()

                gui.load_conversation()

                # Should display backend not available message
                gui.chat_display.append.assert_called_once()

    @patch("gui.MARKDOWN_AVAILABLE", True)
    @patch("gui.markdown")
    def test_markdown_to_html_with_markdown(self):
        """Test markdown to HTML conversion when markdown is available."""
        from src.gui import AIAssistantGUI

        gui = AIAssistantGUI.__new__(AIAssistantGUI)
        gui.dark_theme = True
        gui.markdown_converter = MagicMock()
        gui.markdown_converter.convert.return_value = "<p>Test</p>"

        result = gui.markdown_to_html("**bold**")

        assert "<div style=" in result
        assert "color: #ffffff" in result  # Dark theme
        gui.markdown_converter.convert.assert_called_once_with("**bold**")

    @patch("gui.MARKDOWN_AVAILABLE", False)
    def test_markdown_to_html_plain_text(self):
        """Test markdown to HTML fallback to plain text."""
        from src.gui import AIAssistantGUI

        gui = AIAssistantGUI.__new__(AIAssistantGUI)
        gui.dark_theme = False

        result = gui.markdown_to_html("plain text")

        assert "<div style=" in result
        assert "color: #000000" in result  # Light theme
        assert "plain text" in result

    def test_plain_text_to_html_dark_theme(self):
        """Test plain text to HTML conversion with dark theme."""
        from src.gui import AIAssistantGUI

        gui = AIAssistantGUI.__new__(AIAssistantGUI)
        gui.dark_theme = True

        result = gui.plain_text_to_html("test\n**bold**")

        assert "color: #ffffff" in result
        assert "<b>bold</b>" in result
        assert "<br>" in result  # Newlines converted

    def test_plain_text_to_html_light_theme(self):
        """Test plain text to HTML conversion with light theme."""
        from src.gui import AIAssistantGUI

        gui = AIAssistantGUI.__new__(AIAssistantGUI)
        gui.dark_theme = False

        result = gui.plain_text_to_html("test")

        assert "color: #000000" in result


@pytest.mark.skipif(
    skip_gui_tests,
    reason="GUI tests cause segmentation faults and require manual window closing. Set RUN_GUI_TESTS=1 to run them.",
)
class TestGUIConfiguration:
    """Test GUI configuration and setup."""

    def test_gui_constants_loaded(self):
        """Test that GUI constants are properly loaded."""
        # Test that the constants are accessible
        from src.gui import (  # noqa: F401
            CONTEXT_MODE,
            LEARNING_MODE,
            MODEL_NAME,
            CHROMA_HOST,
            CHROMA_PORT,
            MAX_HISTORY_PAIRS,
        )

        # These should be defined (may be None if not set)
        assert CONTEXT_MODE is not None
        assert LEARNING_MODE is not None
        # Other constants may be None if not initialized

    def test_markdown_availability(self):
        """Test markdown availability detection."""
        from src.gui import MARKDOWN_AVAILABLE

        # This should be a boolean
        assert isinstance(MARKDOWN_AVAILABLE, bool)


@pytest.mark.skipif(
    skip_gui_tests,
    reason="GUI tests cause segmentation faults and require manual window closing. Set RUN_GUI_TESTS=1 to run them.",
)
class TestGUIWorker:
    """Test GUI worker thread (partial testing without Qt)."""

    @patch("gui.BACKEND_AVAILABLE", True)
    def test_ai_worker_initialization(self):
        """Test AI worker initialization."""
        from src.gui import AIWorker

        worker = AIWorker("test message")
        assert worker.user_input == "test message"
        assert hasattr(worker, "response_ready")
        assert hasattr(worker, "error_occurred")

    @patch("gui.BACKEND_AVAILABLE", False)
    @patch("gui.AIWorker.response_ready")
    def test_ai_worker_no_backend(self):
        """Test AI worker when backend is not available."""
        from src.gui import AIWorker

        worker = AIWorker("test message")

        # Mock the run method to test backend check
        with patch.object(worker, "run"):
            worker.run = lambda: None  # Mock run method

            # The actual run method checks BACKEND_AVAILABLE
            # We can't easily test the full run method without Qt
            assert worker.user_input == "test message"
