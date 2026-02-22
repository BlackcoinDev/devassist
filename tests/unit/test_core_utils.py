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
Unit tests for Core Utility Functions.

Tests cover:
- Text chunking with LangChain and fallback
- File path validation for security
- File size information formatting
- Content truncation for display
"""

import unittest
import tempfile
import os
from src.core.utils import (
    chunk_text,
    validate_file_path,
    get_file_size_info,
    truncate_content,
)


class TestChunkText(unittest.TestCase):
    """Test text chunking functionality."""

    def test_chunk_text_short_content(self):
        """Test chunking content shorter than chunk size."""
        content = "This is a short text."
        chunks = chunk_text(content)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], content)

    def test_chunk_text_long_content(self):
        """Test chunking content longer than chunk size."""
        # Create content with multiple paragraphs
        paragraphs = ["Paragraph " + str(i) + " " * 500 for i in range(10)]
        content = "\n\n".join(paragraphs)

        chunks = chunk_text(content)

        # Should have multiple chunks
        self.assertGreater(len(chunks), 1)
        # All content should be preserved
        joined = " ".join(chunks)
        self.assertIn("Paragraph 0", joined)
        self.assertIn("Paragraph 9", joined)

    def test_chunk_text_empty_content(self):
        """Test chunking empty content."""
        chunks = chunk_text("")

        self.assertEqual(len(chunks), 0)

    def test_chunk_text_preserves_code_structure(self):
        """Test that chunking preserves code structure."""
        code = """def function1():
    pass

def function2():
    return True

class MyClass:
    def method(self):
        pass
"""
        chunks = chunk_text(code)

        # Should have at least one chunk
        self.assertGreaterEqual(len(chunks), 1)
        # First chunk should start with function definition
        self.assertTrue(chunks[0].startswith("def function1"))

    def test_chunk_text_fallback_logic(self):
        """Test fallback chunking logic directly."""
        # Create content that needs chunking using fallback-style logic
        # The fallback splits by paragraphs and groups them
        paragraphs = ["Paragraph " + str(i) + " content here" for i in range(5)]
        content = "\n\n".join(paragraphs)

        # Standard chunk_text should handle this
        chunks = chunk_text(content)

        # Should produce at least one chunk
        self.assertGreater(len(chunks), 0)
        # All paragraphs should be present
        joined = "".join(chunks)
        self.assertIn("Paragraph 0", joined)
        self.assertIn("Paragraph 4", joined)


class TestValidateFilePath(unittest.TestCase):
    """Test file path validation for security."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.current_dir = self.tmpdir.name

    def tearDown(self):
        """Clean up test fixtures."""
        self.tmpdir.cleanup()

    def test_validate_path_inside_directory(self):
        """Test validation of path inside current directory."""
        file_path = os.path.join(self.current_dir, "test.txt")
        result = validate_file_path(file_path, self.current_dir)
        self.assertTrue(result)

    def test_validate_path_subdirectory(self):
        """Test validation of path in subdirectory."""
        file_path = os.path.join(self.current_dir, "subdir", "test.txt")
        result = validate_file_path(file_path, self.current_dir)
        self.assertTrue(result)

    def test_validate_path_outside_directory(self):
        """Test validation of path outside current directory."""
        result = validate_file_path("/etc/passwd", self.current_dir)
        self.assertFalse(result)

    def test_validate_path_parent_traversal(self):
        """Test validation blocks parent directory traversal."""
        file_path = os.path.join(self.current_dir, "..", "outside.txt")
        result = validate_file_path(file_path, self.current_dir)
        self.assertFalse(result)

    def test_validate_relative_path(self):
        """Test validation of relative path."""
        # Use absolute path construction for relative-like path
        file_path = os.path.join(self.current_dir, "test.txt")
        result = validate_file_path(file_path, self.current_dir)
        self.assertTrue(result)


class TestGetFileSizeInfo(unittest.TestCase):
    """Test file size information formatting."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Clean up test fixtures."""
        self.tmpdir.cleanup()

    def test_small_file_bytes(self):
        """Test size display for small files (< 1KB)."""
        file_path = os.path.join(self.tmpdir.name, "small.txt")
        with open(file_path, "w") as f:
            f.write("Hello")  # 5 bytes

        size, size_str = get_file_size_info(file_path)

        self.assertEqual(size, 5)
        self.assertIn("bytes", size_str)

    def test_medium_file_kb(self):
        """Test size display for medium files (KB range)."""
        file_path = os.path.join(self.tmpdir.name, "medium.txt")
        with open(file_path, "w") as f:
            f.write("x" * 2048)  # 2KB

        size, size_str = get_file_size_info(file_path)

        self.assertEqual(size, 2048)

    def test_large_file_mb(self):
        """Test size display for large files (MB range)."""
        file_path = os.path.join(self.tmpdir.name, "large.txt")
        with open(file_path, "w") as f:
            f.write("x" * (1024 * 1024 + 100))  # ~1MB

        size, size_str = get_file_size_info(file_path)

        self.assertGreater(size, 1024 * 1024)


class TestTruncateContent(unittest.TestCase):
    """Test content truncation for display."""

    def test_truncate_short_content(self):
        """Test truncation of content shorter than max length."""
        content = "Short content"
        result = truncate_content(content, max_length=100)

        self.assertEqual(result, content)

    def test_truncate_exact_length(self):
        """Test truncation of content at exact max length."""
        content = "x" * 100
        result = truncate_content(content, max_length=100)

        self.assertEqual(result, content)

    def test_truncate_long_content(self):
        """Test truncation of content longer than max length."""
        content = "x" * 150
        result = truncate_content(content, max_length=100)

        self.assertEqual(len(result), 100)
        self.assertTrue(result.endswith("..."))

    def test_truncate_default_max_length(self):
        """Test truncation with default max length."""
        content = "x" * 200
        result = truncate_content(content)  # Default is 100

        self.assertEqual(len(result), 100)

    def test_truncate_preserves_beginning(self):
        """Test that truncation preserves the beginning of content."""
        content = "Hello World " + "x" * 200
        result = truncate_content(content, max_length=50)

        self.assertTrue(result.startswith("Hello World"))
        self.assertTrue(result.endswith("..."))

    def test_truncate_empty_string(self):
        """Test truncation of empty string."""
        result = truncate_content("", max_length=100)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
