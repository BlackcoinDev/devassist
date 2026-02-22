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
Progress display handlers for CLI and GUI modes.

This module provides progress callback implementations for different display modes,
including CLI output, GUI integration, and silent operation for testing.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ProgressCallback(Protocol):
    """
    Protocol interface for progress update callbacks.

    This defines the contract that progress callback objects must implement
    to receive progress updates during auto-learning operations.
    """

    def report_file_start(self, file_path: str) -> None:
        """Report that processing of a file has started."""
        ...

    def report_file_complete(self, file_path: str, success: bool) -> None:
        """Report that processing of a file has completed."""
        ...

    def report_progress(self, message: str) -> None:
        """Report general progress information."""
        ...

    def report_error(self, message: str) -> None:
        """Report an error that occurred during processing."""
        ...

    def report_complete(self, stats: dict) -> None:
        """Report that the entire operation has completed."""
        ...


class CLIProgress:
    """
    CLI progress reporter that outputs to terminal.

    This implementation provides real-time console output with proper
    formatting for terminal display.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize CLI progress reporter.

        Args:
            verbose: Whether to show verbose output (default: True)
        """
        self.verbose = verbose

    def report_file_start(self, file_path: str) -> None:
        """Report that processing of a file has started."""
        if self.verbose:
            print(f"📁 Processing: {file_path}", flush=True)

    def report_file_complete(self, file_path: str, success: bool) -> None:
        """Report that processing of a file has completed."""
        if self.verbose:
            status = "✅" if success else "❌"
            action = "Learned" if success else "Failed"
            print(f"{status} {action}: {file_path}", flush=True)

    def report_progress(self, message: str) -> None:
        """Report general progress information."""
        if self.verbose:
            print(f"📊 {message}", flush=True)

    def report_error(self, message: str) -> None:
        """Report an error that occurred during processing."""
        print(f"❌ Error: {message}", flush=True)

    def report_complete(self, stats: dict) -> None:
        """Report that the entire operation has completed."""
        success_count = stats.get("success_count", 0)
        error_count = stats.get("error_count", 0)
        processed_files = stats.get("processed_files", 0)

        print("\n🎉 Auto-learning completed!", flush=True)
        print(f"   Success: {success_count} files", flush=True)
        print(f"   Errors: {error_count} files", flush=True)
        print(f"   Total processed: {processed_files} files", flush=True)


class GUIProgress:
    """
    GUI progress reporter for future GUI integration.

    This is a placeholder implementation that will be connected to
    the GUI's progress display system in future development.
    """

    def __init__(self, gui_reference=None):
        """
        Initialize GUI progress reporter.

        Args:
            gui_reference: Optional reference to GUI object for direct updates
        """
        self.gui_reference = gui_reference

    def report_file_start(self, file_path: str) -> None:
        """Report that processing of a file has started."""
        # Placeholder for GUI integration
        if self.gui_reference:
            # Would call GUI method like:
            # self.gui_reference.update_progress(f"Processing: {file_path}")
            pass
        else:
            # Fallback to console if no GUI reference
            print(f"[GUI] Processing: {file_path}", flush=True)

    def report_file_complete(self, file_path: str, success: bool) -> None:
        """Report that processing of a file has completed."""
        if self.gui_reference:
            # Would call GUI method like:
            # status = "✅" if success else "❌"
            # self.gui_reference.update_progress(f"{status} {file_path}")
            pass
        else:
            # Fallback to console
            status = "✅" if success else "❌"
            print(f"[GUI] {status}: {file_path}", flush=True)

    def report_progress(self, message: str) -> None:
        """Report general progress information."""
        if self.gui_reference:
            # Would call GUI method like:
            # self.gui_reference.update_progress(message)
            pass
        else:
            # Fallback to console
            print(f"[GUI] {message}", flush=True)

    def report_error(self, message: str) -> None:
        """Report an error that occurred during processing."""
        if self.gui_reference:
            # Would call GUI method like:
            # self.gui_reference.show_error(message)
            pass
        else:
            # Fallback to console
            print(f"[GUI ERROR] {message}", flush=True)

    def report_complete(self, stats: dict) -> None:
        """Report that the entire operation has completed."""
        if self.gui_reference:
            # Would call GUI method like:
            # self.gui_reference.show_completion_stats(stats)
            pass
        else:
            # Fallback to console
            success_count = stats.get("success_count", 0)
            error_count = stats.get("error_count", 0)
            print(
                f"[GUI] Completed: {success_count} success, {error_count} errors",
                flush=True,
            )


class NoOpProgress:
    """
    Silent progress reporter for testing and batch operations.

    This implementation does nothing, useful for automated testing
    and batch operations where output is not desired.
    """

    def report_file_start(self, file_path: str) -> None:
        """Silently ignore file start reports."""
        pass

    def report_file_complete(self, file_path: str, success: bool) -> None:
        """Silently ignore file completion reports."""
        pass

    def report_progress(self, message: str) -> None:
        """Silently ignore progress reports."""
        pass

    def report_error(self, message: str) -> None:
        """Silently ignore error reports."""
        pass

    def report_complete(self, stats: dict) -> None:
        """Silently ignore completion reports."""
        pass
