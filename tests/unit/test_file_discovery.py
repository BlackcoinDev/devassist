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
Test file for file discovery module.

Tests the discover_markdown_files function with various scenarios.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.learning.file_discovery import discover_markdown_files


class TestFileDiscovery:
    """Test cases for file discovery functionality."""

    def test_discovery_basic(self):
        """Test basic markdown file discovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test markdown files
            test_files = [
                "README.md",
                "docs/guide.md",
                "src/AGENTS.md",
                "tests/AGENTS.md",
            ]

            for file_path in test_files:
                full_path = os.path.join(tmpdir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write("# Test content")

            # Discover files
            found_files = discover_markdown_files(tmpdir)

            # Verify all files found
            assert len(found_files) == 4

            # Check specific files
            found_paths = [str(f) for f in found_files]
            assert any("README.md" in p for p in found_paths)
            assert any("docs/guide.md" in p for p in found_paths)
            assert any("src/AGENTS.md" in p for p in found_paths)
            assert any("tests/AGENTS.md" in p for p in found_paths)

    def test_exclusion_directories(self):
        """Test that excluded directories are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files in excluded directories
            excluded_files = [
                ".sisyphus/test.md",
                "__pycache__/cache.md",
                ".git/config.md",
                "node_modules/package.md",
                ".venv/requirements.md",
            ]

            for file_path in excluded_files:
                full_path = os.path.join(tmpdir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write("# Excluded content")

            # Create valid file
            valid_file = os.path.join(tmpdir, "valid.md")
            with open(valid_file, "w") as f:
                f.write("# Valid content")

            # Discover files
            found_files = discover_markdown_files(tmpdir)

            # Should only find the valid file
            assert len(found_files) == 1
            assert "valid.md" in str(found_files[0])

    def test_size_filter(self):
        """Test that large files are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create small file (should be included)
            small_file = os.path.join(tmpdir, "small.md")
            with open(small_file, "w") as f:
                f.write("# Small content")

            # Create large file (should be excluded)
            large_file = os.path.join(tmpdir, "large.md")
            with open(large_file, "w") as f:
                # Create file larger than 5MB
                f.write("# Large content\n" * 500000)  # ~7.5MB

            # Discover files with 5MB limit
            found_files = discover_markdown_files(tmpdir, max_size_mb=5)

            # Should only find the small file
            assert len(found_files) == 1
            assert "small.md" in str(found_files[0])

    def test_nonexistent_directory(self):
        """Test handling of non-existent directory."""
        found_files = discover_markdown_files("/nonexistent/directory")
        assert len(found_files) == 0

    def test_non_directory_path(self):
        """Test handling when path is not a directory."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmpfile:
            found_files = discover_markdown_files(tmpfile.name)
            assert len(found_files) == 0

    def test_empty_directory(self):
        """Test discovery in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            found_files = discover_markdown_files(tmpdir)
            assert len(found_files) == 0

    def test_markdown_extensions(self):
        """Test both .md and .markdown extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with different extensions
            files = [
                "file1.md",
                "file2.markdown",
                "file3.MD",  # Test case insensitivity
                "file4.MARKDOWN",
            ]

            for filename in files:
                full_path = os.path.join(tmpdir, filename)
                with open(full_path, "w") as f:
                    f.write("# Test content")

            # Discover files
            found_files = discover_markdown_files(tmpdir)

            # Should find all markdown files
            assert len(found_files) == 4

    def test_absolute_paths(self):
        """Test that returned paths are absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.md")
            with open(test_file, "w") as f:
                f.write("# Test content")

            # Discover files
            found_files = discover_markdown_files(tmpdir)

            # Check that path is absolute
            assert len(found_files) == 1
            assert found_files[0].is_absolute()

    @patch("src.learning.file_discovery.logger")
    def test_logging(self, mock_logger):
        """Test that logging is working correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.md")
            with open(test_file, "w") as f:
                f.write("# Test content")

            # Discover files
            found_files = discover_markdown_files(tmpdir)

            # Verify logging calls
            mock_logger.info.assert_called_once()
            mock_logger.debug.assert_called_once()

    def test_custom_exclude_dirs(self):
        """Test custom exclude directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files in custom excluded directory
            custom_dir = os.path.join(tmpdir, "custom_exclude")
            os.makedirs(custom_dir)
            custom_file = os.path.join(custom_dir, "test.md")
            with open(custom_file, "w") as f:
                f.write("# Test content")

            # Create valid file
            valid_file = os.path.join(tmpdir, "valid.md")
            with open(valid_file, "w") as f:
                f.write("# Valid content")

            # Discover files with custom exclusion
            exclude_dirs = [
                ".sisyphus",
                "__pycache__",
                ".git",
                "node_modules",
                ".venv",
                "custom_exclude",
            ]
            found_files = discover_markdown_files(tmpdir, exclude_dirs=exclude_dirs)

            # Should only find the valid file
            assert len(found_files) == 1
            assert "valid.md" in str(found_files[0])

    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            test_file = os.path.join(tmpdir, "test.md")
            with open(test_file, "w") as f:
                f.write("# Test content")

            # Mock permission error for specific file
            def mock_getsize(path):
                if "test.md" in path:
                    raise PermissionError("Permission denied")
                return 100

            with patch("os.path.getsize", side_effect=mock_getsize):
                found_files = discover_markdown_files(tmpdir)

                # Should handle error gracefully and return empty list
                assert len(found_files) == 0

    def test_mixed_file_types(self):
        """Test discovery with mixed file types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create various file types
            files = [
                ("test.md", "# Markdown content"),
                ("test.txt", "Plain text content"),
                ("test.py", "# Python code"),
                ("test.json", '{"key": "value"}'),
                ("readme.MARKDOWN", "# Another markdown"),
            ]

            for filename, content in files:
                full_path = os.path.join(tmpdir, filename)
                with open(full_path, "w") as f:
                    f.write(content)

            # Discover files
            found_files = discover_markdown_files(tmpdir)

            # Should only find markdown files
            assert len(found_files) == 2
            found_filenames = [f.name for f in found_files]
            assert "test.md" in found_filenames
            assert "readme.MARKDOWN" in found_filenames
            assert "test.txt" not in found_filenames
            assert "test.py" not in found_filenames
            assert "test.json" not in found_filenames
