#!/usr/bin/env python3
"""
System Tools Tests

Tests for code_search tool:
- Pattern search with ripgrep
- File type filtering
- Path validation
- Result parsing
"""

import json
from unittest.mock import patch, MagicMock
import subprocess

from src.tools.executors.system_tools import execute_code_search


class TestCodeSearchBasic:
    """Test basic code search functionality."""

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_success(self, mock_exists, mock_getcwd, mock_run, mock_which):
        """Test successful code search."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True

        # Ripgrep JSON output format
        rg_output = json.dumps({
            "type": "match",
            "data": {
                "path": {"text": "/tmp/project/src/main.py"},
                "line_number": 10,
                "lines": {"text": "def main():\n"},
                "submatches": [{"match": {"text": "main"}}]
            }
        })

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=rg_output,
            stderr=""
        )

        result = execute_code_search("main")

        assert result["success"] is True
        assert result["match_count"] == 1
        assert result["matches"][0]["file"] == "src/main.py"
        assert result["matches"][0]["line"] == 10

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_no_matches(self, mock_exists, mock_getcwd, mock_run, mock_which):
        """Test search with no matches."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True

        # Return code 1 = no matches (not an error for rg)
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr=""
        )

        result = execute_code_search("nonexistent_pattern_xyz")

        assert result["success"] is True
        assert result["match_count"] == 0
        assert result["matches"] == []

    @patch("shutil.which")
    def test_code_search_empty_pattern(self, mock_which):
        """Test search with empty pattern."""
        mock_which.return_value = "/usr/bin/rg"

        result = execute_code_search("")

        assert "error" in result
        assert "cannot be empty" in result["error"]


class TestCodeSearchRipgrepRequired:
    """Test ripgrep requirement."""

    @patch("shutil.which")
    def test_code_search_ripgrep_not_installed(self, mock_which):
        """Test error when ripgrep is not installed."""
        mock_which.return_value = None

        result = execute_code_search("pattern")

        assert "error" in result
        assert "ripgrep" in result["error"].lower()
        assert "not installed" in result["error"].lower()


class TestCodeSearchPathValidation:
    """Test path security validation."""

    @patch("shutil.which")
    @patch("os.getcwd")
    @patch("os.path.abspath")
    def test_code_search_path_traversal_blocked(
        self, mock_abspath, mock_getcwd, mock_which
    ):
        """Test that path traversal is blocked."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/home/user/project"
        mock_abspath.return_value = "/etc/passwd"  # Outside project

        result = execute_code_search("pattern", path="../../etc")

        assert "error" in result
        assert "Access denied" in result["error"]

    @patch("shutil.which")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_path_not_found(self, mock_exists, mock_getcwd, mock_which):
        """Test error when search path doesn't exist."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = False

        result = execute_code_search("pattern", path="nonexistent_dir")

        assert "error" in result
        assert "not found" in result["error"].lower()


class TestCodeSearchFileTypeFilter:
    """Test file type filtering."""

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_with_file_type(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test search with file type filter."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        execute_code_search("pattern", file_type="py")

        # Check that --type=py was passed
        call_args = mock_run.call_args[0][0]
        assert "--type=py" in call_args

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_result_includes_file_type(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test that result includes file_type parameter."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        result = execute_code_search("pattern", file_type="js")

        assert result["file_type"] == "js"


class TestCodeSearchCaseSensitivity:
    """Test case sensitivity options."""

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_case_insensitive_default(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test that search is case-insensitive by default."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        execute_code_search("Pattern")

        call_args = mock_run.call_args[0][0]
        assert "--ignore-case" in call_args

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_case_sensitive(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test case-sensitive search."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        execute_code_search("Pattern", case_sensitive=True)

        call_args = mock_run.call_args[0][0]
        assert "--ignore-case" not in call_args


class TestCodeSearchMaxResults:
    """Test max results limiting."""

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_max_results_passed(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test that max_results is passed to ripgrep."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        execute_code_search("pattern", max_results=25)

        call_args = mock_run.call_args[0][0]
        assert "--max-count=25" in call_args

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_max_results_clamped_to_max(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test that max_results is clamped to 200."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")

        execute_code_search("pattern", max_results=500)

        call_args = mock_run.call_args[0][0]
        assert "--max-count=200" in call_args

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_result_truncation(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test that results are truncated when exceeding max_results."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True

        # Create 10 matches
        matches = []
        for i in range(10):
            matches.append(json.dumps({
                "type": "match",
                "data": {
                    "path": {"text": f"/tmp/project/file{i}.py"},
                    "line_number": i + 1,
                    "lines": {"text": f"line {i}\n"},
                    "submatches": [{"match": {"text": "pattern"}}]
                }
            }))

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="\n".join(matches),
            stderr=""
        )

        result = execute_code_search("pattern", max_results=5)

        assert result["match_count"] == 5
        assert result["total_found"] == 10
        assert result["truncated"] is True


class TestCodeSearchErrorHandling:
    """Test error handling."""

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_timeout(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test timeout handling."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("rg", 60)

        result = execute_code_search("pattern")

        assert "error" in result
        assert "timed out" in result["error"].lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_ripgrep_error(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test ripgrep error handling."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(
            returncode=2,  # Error code
            stdout="",
            stderr="rg: unrecognized option"
        )

        result = execute_code_search("pattern")

        assert "error" in result
        assert "failed" in result["error"].lower()

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_general_exception(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test general exception handling."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True
        mock_run.side_effect = Exception("Unexpected error")

        result = execute_code_search("pattern")

        assert "error" in result
        assert "Unexpected error" in result["error"]


class TestCodeSearchOutputParsing:
    """Test JSON output parsing from ripgrep."""

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_parses_multiple_matches(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test parsing multiple match results."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True

        matches = [
            json.dumps({
                "type": "match",
                "data": {
                    "path": {"text": "/tmp/project/a.py"},
                    "line_number": 1,
                    "lines": {"text": "def foo():\n"},
                    "submatches": [{"match": {"text": "foo"}}]
                }
            }),
            json.dumps({
                "type": "match",
                "data": {
                    "path": {"text": "/tmp/project/b.py"},
                    "line_number": 5,
                    "lines": {"text": "def bar():\n"},
                    "submatches": [{"match": {"text": "bar"}}]
                }
            }),
        ]

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="\n".join(matches),
            stderr=""
        )

        result = execute_code_search("def")

        assert result["match_count"] == 2
        assert result["matches"][0]["file"] == "a.py"
        assert result["matches"][1]["file"] == "b.py"

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_ignores_non_match_entries(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test that non-match JSON entries are ignored."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True

        output = "\n".join([
            json.dumps({"type": "begin", "data": {"path": {"text": "file.py"}}}),
            json.dumps({
                "type": "match",
                "data": {
                    "path": {"text": "/tmp/project/file.py"},
                    "line_number": 1,
                    "lines": {"text": "content\n"},
                    "submatches": []
                }
            }),
            json.dumps({"type": "end", "data": {"path": {"text": "file.py"}}}),
        ])

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=output,
            stderr=""
        )

        result = execute_code_search("content")

        # Should only count the match, not begin/end
        assert result["match_count"] == 1

    @patch("shutil.which")
    @patch("subprocess.run")
    @patch("os.getcwd")
    @patch("os.path.exists")
    def test_code_search_handles_malformed_json(
        self, mock_exists, mock_getcwd, mock_run, mock_which
    ):
        """Test handling of malformed JSON lines."""
        mock_which.return_value = "/usr/bin/rg"
        mock_getcwd.return_value = "/tmp/project"
        mock_exists.return_value = True

        output = "not valid json\n" + json.dumps({
            "type": "match",
            "data": {
                "path": {"text": "/tmp/project/file.py"},
                "line_number": 1,
                "lines": {"text": "content\n"},
                "submatches": []
            }
        })

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=output,
            stderr=""
        )

        result = execute_code_search("content")

        # Should successfully parse the valid match, skip invalid line
        assert result["success"] is True
        assert result["match_count"] == 1
