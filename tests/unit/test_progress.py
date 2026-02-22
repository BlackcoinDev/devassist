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

from src.learning.progress import CLIProgress, GUIProgress, NoOpProgress


class TestCLIProgress:
    """Test CLI progress reporter functionality."""

    def test_cli_progress_file_start(self):
        """Test that CLIProgress outputs file start message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_called_with("📁 Processing: /path/to/file.md", flush=True)

    def test_cli_progress_file_start_quiet(self):
        """Test that CLIProgress in quiet mode doesn't output file start message."""
        progress = CLIProgress(verbose=False)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_not_called()

    def test_cli_progress_file_complete_success(self):
        """Test that CLIProgress outputs successful file completion message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_called_with("✅ Learned: /path/to/file.md", flush=True)

    def test_cli_progress_file_complete_failure(self):
        """Test that CLIProgress outputs failed file completion message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=False)
            mock_print.assert_called_with("❌ Failed: /path/to/file.md", flush=True)

    def test_cli_progress_file_complete_quiet(self):
        """Test that CLIProgress in quiet mode doesn't output file completion message."""
        progress = CLIProgress(verbose=False)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_not_called()

    def test_cli_progress_progress_message(self):
        """Test that CLIProgress outputs progress message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_progress("Processing files...")
            mock_print.assert_called_with("📊 Processing files...", flush=True)

    def test_cli_progress_error_message(self):
        """Test that CLIProgress outputs error message."""
        progress = CLIProgress(verbose=True)

        with patch("builtins.print") as mock_print:
            progress.report_error("File not found")
            mock_print.assert_called_with("❌ Error: File not found", flush=True)

    def test_cli_progress_complete(self):
        """Test that CLIProgress outputs completion summary."""
        progress = CLIProgress(verbose=True)
        stats = {"success_count": 5, "error_count": 2, "processed_files": 7}

        with patch("builtins.print") as mock_print:
            progress.report_complete(stats)

            # Verify all expected calls were made
            calls = mock_print.call_args_list
            assert len(calls) == 4

            # Check first call (completion message)
            assert calls[0][0][0] == "\n🎉 Auto-learning completed!"

            # Check success count
            assert "Success: 5 files" in calls[1][0][0]

            # Check error count
            assert "Errors: 2 files" in calls[2][0][0]

            # Check total processed
            assert "Total processed: 7 files" in calls[3][0][0]


class TestGUIProgress:
    """Test GUI progress reporter functionality."""

    def test_gui_progress_file_start_no_reference(self):
        """Test that GUIProgress without reference falls back to console."""
        progress = GUIProgress(gui_reference=None)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_called_with(
                "[GUI] Processing: /path/to/file.md", flush=True
            )

    def test_gui_progress_file_start_with_reference(self):
        """Test that GUIProgress with reference doesn't call print."""
        mock_gui = Mock()
        progress = GUIProgress(gui_reference=mock_gui)

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            # Should not call print when GUI reference is available
            mock_print.assert_not_called()

    def test_gui_progress_file_complete_no_reference(self):
        """Test that GUIProgress without reference falls back to console for completion."""
        progress = GUIProgress(gui_reference=None)

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_called_with("[GUI] ✅: /path/to/file.md", flush=True)

    def test_gui_progress_error_no_reference(self):
        """Test that GUIProgress without reference falls back to console for errors."""
        progress = GUIProgress(gui_reference=None)

        with patch("builtins.print") as mock_print:
            progress.report_error("File not found")
            mock_print.assert_called_with("[GUI ERROR] File not found", flush=True)

    def test_gui_progress_complete_no_reference(self):
        """Test that GUIProgress without reference falls back to console for completion."""
        progress = GUIProgress(gui_reference=None)
        stats = {"success_count": 3, "error_count": 1}

        with patch("builtins.print") as mock_print:
            progress.report_complete(stats)
            mock_print.assert_called_with(
                "[GUI] Completed: 3 success, 1 errors", flush=True
            )


class TestNoOpProgress:
    """Test NoOp progress reporter functionality."""

    def test_noop_progress_file_start(self):
        """Test that NoOpProgress doesn't output anything for file start."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_file_start("/path/to/file.md")
            mock_print.assert_not_called()

    def test_noop_progress_file_complete(self):
        """Test that NoOpProgress doesn't output anything for file completion."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_file_complete("/path/to/file.md", success=True)
            mock_print.assert_not_called()

    def test_noop_progress_progress(self):
        """Test that NoOpProgress doesn't output anything for progress."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_progress("Processing files...")
            mock_print.assert_not_called()

    def test_noop_progress_error(self):
        """Test that NoOpProgress doesn't output anything for errors."""
        progress = NoOpProgress()

        with patch("builtins.print") as mock_print:
            progress.report_error("File not found")
            mock_print.assert_not_called()

    def test_noop_progress_complete(self):
        """Test that NoOpProgress doesn't output anything for completion."""
        progress = NoOpProgress()
        stats = {"success_count": 5, "error_count": 2, "processed_files": 7}

        with patch("builtins.print") as mock_print:
            progress.report_complete(stats)
            mock_print.assert_not_called()


class TestProgressIntegration:
    """Test integration scenarios with progress callbacks."""

    def test_cli_progress_stdout_capture(self):
        """Test that CLIProgress actually writes to stdout."""
        progress = CLIProgress(verbose=True)

        # Capture stdout
        captured_output = io.StringIO()

        with patch("sys.stdout", new=captured_output):
            progress.report_file_start("/test/file.md")
            progress.report_progress("Processing...")
            progress.report_file_complete("/test/file.md", success=True)
            progress.report_error("Test error")

        output = captured_output.getvalue()

        # Verify expected content is in output
        assert "📁 Processing: /test/file.md" in output
        assert "📊 Processing..." in output
        assert "✅ Learned: /test/file.md" in output
        assert "❌ Error: Test error" in output

    def test_progress_callback_protocol_compliance(self):
        """Test that all progress classes implement the ProgressCallback protocol."""
        from src.learning.progress import ProgressCallback

        # Test that CLIProgress implements ProgressCallback
        cli_progress = CLIProgress()
        assert isinstance(cli_progress, ProgressCallback)

        # Test that GUIProgress implements ProgressCallback
        gui_progress = GUIProgress()
        assert isinstance(gui_progress, ProgressCallback)

        # Test that NoOpProgress implements ProgressCallback
        noop_progress = NoOpProgress()
        assert isinstance(noop_progress, ProgressCallback)
