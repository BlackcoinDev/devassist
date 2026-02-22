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
Tests for /approve command and ToolApprovalManager set_policy.
"""

from unittest.mock import patch, mock_open
from src.commands.handlers.config_commands import handle_approve
from src.tools.approval import ToolApprovalManager


class TestApproveCommand:
    @patch("src.tools.approval.ToolApprovalManager.set_policy")
    @patch("builtins.print")
    def test_handle_approve_success(self, mock_print, mock_set_policy):
        """Test successful policy update via command."""
        mock_set_policy.return_value = True
        handle_approve(["shell_execute", "always"])

        mock_set_policy.assert_called_once_with("shell_execute", "always")
        # Check that success message was printed
        args, _ = mock_print.call_args_list[-1]
        assert "set to: always" in args[0]

    @patch("src.tools.approval.ToolApprovalManager.set_policy")
    @patch("builtins.print")
    def test_handle_approve_invalid_args(self, mock_print, mock_set_policy):
        """Test command with missing arguments."""
        handle_approve(["only_one_arg"])
        # Should print usage/help
        args, _ = mock_print.call_args_list[0]
        assert "Tool Approval Management" in args[0]
        mock_set_policy.assert_not_called()

    @patch("builtins.open", new_callable=mock_open)
    @patch("src.tools.approval.Path.exists")
    def test_set_policy_persistence(self, mock_exists, mock_file):
        """Test that set_policy writes to config file."""
        mock_exists.return_value = True
        # Mock file content for initial load
        mock_file.return_value.read.return_value = '{"approvals": {}}'

        manager = ToolApprovalManager()
        result = manager.set_policy("read_file", "always")

        assert result is True
        assert manager.approvals["read_file"] == "always"
        # Verify write call
        mock_file().write.assert_called()
