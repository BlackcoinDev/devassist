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
Git Tools Tests

Tests for git tools:
- git_status: Repository status
- git_diff: Change diffs
- git_log: Commit history

Mock pattern: Patch run_git_command at import location in git_tools.py.
Return dicts with keys: success, stdout, stderr, returncode.
"""

from unittest.mock import patch


from src.tools.executors.git_tools import (
    execute_git_status,
    execute_git_diff,
    execute_git_log,
)


class TestGitStatus:
    """Test git_status tool."""

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_status_clean_repo(self, mock_getcwd, mock_run_git):
        """Test status of clean repository."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "main\n", "stderr": ""},
        ]
        result = execute_git_status()
        assert result["success"] is True
        assert result["is_clean"] is True
        assert result["branch"] == "main"
        assert result["staged_count"] == 0
        assert result["unstaged_count"] == 0
        assert result["untracked_count"] == 0

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_status_with_changes(self, mock_getcwd, mock_run_git):
        """Test status with staged, unstaged, and untracked files."""
        mock_getcwd.return_value = "/tmp/repo"
        status_output = "M  staged.txt\n M unstaged.txt\n?? untracked.txt\n"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": status_output, "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "develop\n", "stderr": ""},
        ]
        result = execute_git_status()
        assert result["success"] is True
        assert result["is_clean"] is False
        assert result["branch"] == "develop"
        assert result["staged_count"] == 1
        assert result["unstaged_count"] == 1
        assert result["untracked_count"] == 1

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_status_not_a_repo(self, mock_getcwd, mock_run_git):
        """Test status when not in a git repository."""
        mock_getcwd.return_value = "/tmp/not-a-repo"
        mock_run_git.return_value = {
            "success": False,
            "returncode": 128,
            "stdout": "",
            "stderr": "fatal: not a git repository",
        }
        result = execute_git_status()
        assert "error" in result
        assert "Not a git repository" in result["error"]

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_status_git_not_installed(self, mock_getcwd, mock_run_git):
        """Test status when git is not installed."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.return_value = {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "git not found",
        }
        result = execute_git_status()
        assert "error" in result
        assert "Not a git repository" in result["error"]


class TestGitDiff:
    """Test git_diff tool."""

    @patch("src.tools.executors.git_tools.run_git_command", autospec=True)
    @patch("os.getcwd")
    def test_git_diff_with_changes(self, mock_getcwd, mock_run):
        """Test diff with unstaged changes."""
        mock_getcwd.return_value = "/tmp/repo"
        diff_output = """diff --git a/file.txt b/file.txt
index 1234567..abcdefg 100644
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,4 @@
 line 1
+new line
 line 2
"""
        mock_run.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": diff_output, "stderr": ""},
        ]
        result = execute_git_diff()

        assert result["success"] is True
        assert result["has_changes"] is True
        assert "+new line" in result["diff"]
        assert result["staged"] is False

    @patch("src.tools.executors.git_tools.run_git_command", autospec=True)
    @patch("os.getcwd")
    def test_git_diff_staged_changes(self, mock_getcwd, mock_run):
        """Test diff with staged changes."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {
                "success": True,
                "returncode": 0,
                "stdout": "staged diff content\n",
                "stderr": "",
            },
        ]
        result = execute_git_diff(staged=True)

        assert result["success"] is True
        assert result["staged"] is True

    @patch("src.tools.executors.git_tools.run_git_command", autospec=True)
    @patch("os.getcwd")
    def test_git_diff_specific_file(self, mock_getcwd, mock_run):
        """Test diff for specific file."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "file diff\n", "stderr": ""},
        ]
        result = execute_git_diff(file_path="src/main.py")
        assert result["success"] is True
        assert result["file_path"] == "src/main.py"

    @patch("src.tools.executors.git_tools.run_git_command", autospec=True)
    @patch("os.getcwd")
    def test_git_diff_no_changes(self, mock_getcwd, mock_run):
        """Test diff with no changes."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "", "stderr": ""},
        ]
        result = execute_git_diff()
        assert result["success"] is True
        assert result["has_changes"] is False
        assert "No unstaged changes" in result["message"]

    @patch("src.tools.executors.git_tools.run_git_command", autospec=True)
    @patch("os.getcwd")
    def test_git_diff_not_a_repo(self, mock_getcwd, mock_run):
        """Test diff when not in a git repository."""
        mock_getcwd.return_value = "/tmp/not-a-repo"
        mock_run.return_value = {
            "success": False,
            "returncode": 128,
            "stdout": "",
            "stderr": "",
        }
        result = execute_git_diff()
        assert "error" in result

    @patch("src.tools.executors.git_tools.run_git_command", autospec=True)
    @patch("os.getcwd")
    def test_git_diff_truncation(self, mock_getcwd, mock_run):
        """Test that large diffs are truncated."""
        mock_getcwd.return_value = "/tmp/repo"
        large_diff = "x" * (150 * 1024)
        mock_run.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": large_diff, "stderr": ""},
        ]
        result = execute_git_diff()
        assert result["success"] is True
        assert result["truncated"] is True
        assert len(result["diff"]) < len(large_diff)


class TestGitLog:
    """Test git_log tool."""

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_basic(self, mock_getcwd, mock_run_git):
        """Test basic git log."""
        mock_getcwd.return_value = "/tmp/repo"
        log_output = """abc1234|John Doe|2024-01-15|Initial commit
def5678|Jane Smith|2024-01-16|Add feature"""
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": log_output, "stderr": ""},
        ]
        result = execute_git_log()
        assert result["success"] is True
        assert result["commit_count"] == 2
        assert len(result["commits"]) == 2
        assert result["commits"][0]["hash"] == "abc1234"
        assert result["commits"][0]["author"] == "John Doe"
        assert result["commits"][0]["message"] == "Initial commit"

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_with_limit(self, mock_getcwd, mock_run_git):
        """Test git log with custom limit."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {
                "success": True,
                "returncode": 0,
                "stdout": "abc|Author|2024-01-01|Msg",
                "stderr": "",
            },
        ]
        execute_git_log(limit=5)
        second_call_args = mock_run_git.call_args_list[1][0][0]
        assert "-n5" in second_call_args

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_for_specific_file(self, mock_getcwd, mock_run_git):
        """Test git log for specific file."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {
                "success": True,
                "returncode": 0,
                "stdout": "abc|Author|2024-01-01|Msg",
                "stderr": "",
            },
        ]
        result = execute_git_log(file_path="src/main.py")
        assert result["file_path"] == "src/main.py"
        second_call_args = mock_run_git.call_args_list[1][0][0]
        assert "/tmp/repo/src/main.py" in second_call_args

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_limit_clamped_to_max(self, mock_getcwd, mock_run_git):
        """Test that limit is clamped to maximum (100)."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "", "stderr": ""},
        ]
        execute_git_log(limit=500)
        second_call_args = mock_run_git.call_args_list[1][0][0]
        assert "-n100" in second_call_args

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_limit_clamped_to_min(self, mock_getcwd, mock_run_git):
        """Test that negative limit defaults to 10."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "", "stderr": ""},
        ]
        execute_git_log(limit=-5)
        second_call_args = mock_run_git.call_args_list[1][0][0]
        assert "-n10" in second_call_args

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_not_a_repo(self, mock_getcwd, mock_run_git):
        """Test log when not in a git repository."""
        mock_getcwd.return_value = "/tmp/not-a-repo"
        mock_run_git.return_value = {
            "success": False,
            "returncode": 128,
            "stdout": "",
            "stderr": "",
        }
        result = execute_git_log()
        assert "error" in result

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_log_empty_repo(self, mock_getcwd, mock_run_git):
        """Test log for repository with no commits."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "", "stderr": ""},
        ]
        result = execute_git_log()
        assert result["success"] is True
        assert result["commit_count"] == 0
        assert result["commits"] == []


class TestGitToolsEdgeCases:
    """Test edge cases and error handling."""

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_timeout(self, mock_getcwd, mock_run_git):
        """Test timeout handling for git commands."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": False, "returncode": -1, "stdout": "", "stderr": "timed out"},
        ]
        result = execute_git_status()
        assert "error" in result
        assert "timed out" in result["error"].lower()

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_general_exception(self, mock_getcwd, mock_run_git):
        """Test general exception handling."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": False, "returncode": -1, "stdout": "", "stderr": "Unexpected error"},
        ]
        result = execute_git_diff()
        assert "error" in result

    @patch("src.tools.executors.git_tools.run_git_command")
    @patch("os.getcwd")
    def test_git_status_malformed_output(self, mock_getcwd, mock_run_git):
        """Test handling of malformed git status output."""
        mock_getcwd.return_value = "/tmp/repo"
        mock_run_git.side_effect = [
            {"success": True, "returncode": 0, "stdout": ".git\n", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "X\nAB", "stderr": ""},
            {"success": True, "returncode": 0, "stdout": "main\n", "stderr": ""},
        ]
        result = execute_git_status()
        assert result["success"] is True
