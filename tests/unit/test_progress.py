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
Test cases for progress display handlers.

This module tests the CLI, GUI, and NoOp progress callback implementations.
"""

import io
from unittest.mock import patch, Mock

from src.learning.progress import CLIProgress, GUIProgress, NoOpProgress


class TestCLIProgress:
    """Test CLI progress reporter functionality."""

    def test_cli_progress_file_start(self):
        """Test that CLIProgress outputs file start message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_called()

    def test_cli_progress_file_start_quiet(self):
        """Test CLIProgress in quiet mode does not output start message."""
        progress = CLIProgress(verbose=False)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_not_called()

    def test_cli_progress_file_complete_success(self):
        """Test CLIProgress outputs successful file completion message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_called()

    def test_cli_progress_file_complete_failure(self):
        """Test CLIProgress outputs failure file completion message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=False)
            mock_print.assert_called()

    def test_cli_progress_file_complete_quiet(self):
        """Test CLIProgress in quiet mode for completion."""
        progress = CLIProgress(verbose=False)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_not_called()

    def test_cli_progress_progress_message(self):
        """Test CLIProgress outputs progress message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_progress("Processing file 5 of 10")
            mock_print.assert_called()

    def test_cli_progress_error_message(self):
        """Test CLIProgress outputs error message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_error("File not found")
            mock_print.assert_called()

    def test_cli_progress_complete(self):
        """Test CLIProgress outputs completion message."""
        progress = CLIProgress(verbose=True)
        stats = {"success_count": 5, "error_count": 2}

        with patch("builtins.print") as mock_print:
            progress.report_complete(stats)
            mock_print.assert_called()


class TestGUIProgress:
    """Test GUI progress reporter functionality."""

    def test_gui_progress_file_start_no_reference(self):
        """Test GUIProgress without reference falls back to console."""
        progress = GUIProgress(gui_reference=None)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_called()

    def test_gui_progress_file_start_with_reference(self):
        """Test GUIProgress with reference does not call print."""
        mock_gui = Mock()
        progress = GUIProgress(gui_reference=mock_gui)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_not_called()

    def test_gui_progress_file_complete_no_reference(self):
        """Test GUIProgress without reference falls back to console."""
        progress = GUIProgress(gui_reference=None)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_called()

    def test_gui_progress_error_no_reference(self):
        """Test GUIProgress without reference falls back to console."""
        progress = GUIProgress(gui_reference=None)

        with patch("builtins.print") as mock_print:
            progress.report_error("File not found")
            mock_print.assert_called()

    def test_gui_progress_complete_no_reference(self):
        """Test GUIProgress without reference falls back to console."""
        progress = GUIProgress(gui_reference=None)
        stats = {"success_count": 3, "error_count": 1}

        with patch("builtins.print") as mock_print:
            progress.report_complete(stats)
            mock_print.assert_called()


class TestNoOpProgress:
    """Test NoOp progress reporter functionality."""

    def test_noop_progress_file_start(self):
        """Test NoOpProgress does not output file start message."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_not_called()

    def test_noop_progress_file_complete(self):
        """Test NoOpProgress does not output file complete message."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_not_called()

    def test_noop_progress_progress(self):
        """Test NoOpProgress does not output progress message."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_progress("Processing file 5 of 10")
            mock_print.assert_not_called()

    def test_noop_progress_error(self):
        """Test NoOpProgress does not output error message."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_error("File not found")
            mock_print.assert_not_called()

    def test_noop_progress_complete(self):
        """Test NoOpProgress does not output complete message."""
        progress = NoOpProgress()
        stats = {"success_count": 5, "error_count": 2}

        with patch("builtins.print") as mock_print:
            progress.report_complete(stats)
            mock_print.assert_not_called()


class TestProgressIntegration:
    """Test progress callback integration."""

    def test_cli_progress_stdout_capture(self):
        """Test that CLIProgress writes to stdout."""
        captured_output = io.StringIO()

        with patch("sys.stdout", new=captured_output):
            progress = CLIProgress(verbose=True)
            progress.report_file_start("/test/file.md")

        output = captured_output.getvalue()
        assert "Processing" in output

    def test_progress_callback_protocol_compliance(self):
        """Test that all progress classes implement the same interface."""
        methods = [
            "report_file_start",
            "report_file_complete",
            "report_progress",
            "report_error",
            "report_complete",
        ]

        for cls in [CLIProgress, GUIProgress, NoOpProgress]:
            for method in methods:
                assert hasattr(cls, method)
                assert callable(getattr(cls, method))
