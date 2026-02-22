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
Unit tests for File Operation Commands.

Tests cover:
- Read file operations (success, errors, security)
- Write file operations (success, errors, security)
- List directory operations (success, errors, security)
- PWD operations
"""

import unittest
import tempfile
import os
from io import StringIO
import sys
from src.commands.handlers.file_commands import (
    handle_read,
    handle_write,
    handle_list,
    handle_pwd,
)


class TestHandleRead(unittest.TestCase):
    """Test /read command handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    def test_read_no_args(self):
        """Test /read with no arguments shows usage."""
        captured = StringIO()
        sys.stdout = captured
        handle_read([])
        sys.stdout = sys.__stdout__

        self.assertIn("Usage:", captured.getvalue())
        self.assertIn("/read <file_path>", captured.getvalue())

    def test_read_file_success(self):
        """Test reading a valid file."""
        # Create test file
        test_content = "Hello, World!\nLine 2"
        with open("test.txt", "w") as f:
            f.write(test_content)

        captured = StringIO()
        sys.stdout = captured
        handle_read(["test.txt"])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Hello, World!", output)
        self.assertIn("Line 2", output)
        self.assertIn("File read successfully", output)

    def test_read_file_not_found(self):
        """Test reading a non-existent file."""
        captured = StringIO()
        sys.stdout = captured
        handle_read(["nonexistent.txt"])
        sys.stdout = sys.__stdout__

        self.assertIn("File not found", captured.getvalue())

    def test_read_directory_not_file(self):
        """Test reading a directory instead of file."""
        os.mkdir("testdir")

        captured = StringIO()
        sys.stdout = captured
        handle_read(["testdir"])
        sys.stdout = sys.__stdout__

        self.assertIn("Not a file", captured.getvalue())

    def test_read_file_outside_directory(self):
        """Test security: cannot read files outside current directory."""
        captured = StringIO()
        sys.stdout = captured
        handle_read(["/etc/passwd"])
        sys.stdout = sys.__stdout__

        self.assertIn("Access denied", captured.getvalue())

    def test_read_file_too_large(self):
        """Test reading a file that exceeds size limit."""
        # Create a file larger than 1MB
        large_content = "x" * (1024 * 1024 + 100)
        with open("large.txt", "w") as f:
            f.write(large_content)

        captured = StringIO()
        sys.stdout = captured
        handle_read(["large.txt"])
        sys.stdout = sys.__stdout__

        self.assertIn("File too large", captured.getvalue())

    def test_read_file_with_spaces_in_name(self):
        """Test reading file with spaces in name."""
        test_content = "Content with spaces"
        with open("my file.txt", "w") as f:
            f.write(test_content)

        captured = StringIO()
        sys.stdout = captured
        handle_read(["my", "file.txt"])  # Args come as list
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Content with spaces", output)


class TestHandleWrite(unittest.TestCase):
    """Test /write command handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    def test_write_no_args(self):
        """Test /write with no arguments shows usage."""
        captured = StringIO()
        sys.stdout = captured
        handle_write([])
        sys.stdout = sys.__stdout__

        self.assertIn("Usage:", captured.getvalue())

    def test_write_no_content(self):
        """Test /write with file path but no content."""
        captured = StringIO()
        sys.stdout = captured
        handle_write(["test.txt"])
        sys.stdout = sys.__stdout__

        self.assertIn("Content is required", captured.getvalue())

    def test_write_file_success(self):
        """Test writing a file successfully."""
        captured = StringIO()
        sys.stdout = captured
        handle_write(["test.txt", "Hello", "World"])
        sys.stdout = sys.__stdout__

        self.assertIn("File written", captured.getvalue())

        # Verify file was created
        self.assertTrue(os.path.exists("test.txt"))
        with open("test.txt", "r") as f:
            content = f.read()
        self.assertEqual(content, "Hello World")

    def test_write_creates_directory(self):
        """Test that /write creates parent directories."""
        captured = StringIO()
        sys.stdout = captured
        handle_write(["subdir/test.txt", "Content"])
        sys.stdout = sys.__stdout__

        self.assertIn("File written", captured.getvalue())
        self.assertTrue(os.path.exists("subdir/test.txt"))

    def test_write_outside_directory(self):
        """Test security: cannot write files outside current directory."""
        captured = StringIO()
        sys.stdout = captured
        handle_write(["/tmp/outside.txt", "Content"])
        sys.stdout = sys.__stdout__

        self.assertIn("Access denied", captured.getvalue())


class TestHandleList(unittest.TestCase):
    """Test /list command handler."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_cwd = os.getcwd()
        self.tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)
        self.tmpdir.cleanup()

    def test_list_current_directory(self):
        """Test listing current directory."""
        # Create test files
        with open("file1.txt", "w") as f:
            f.write("test")
        os.mkdir("subdir")

        captured = StringIO()
        sys.stdout = captured
        handle_list([])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("file1.txt", output)
        self.assertIn("subdir/", output)

    def test_list_subdirectory(self):
        """Test listing a subdirectory."""
        os.mkdir("testdir")
        with open("testdir/nested.txt", "w") as f:
            f.write("test")

        captured = StringIO()
        sys.stdout = captured
        handle_list(["testdir"])
        sys.stdout = sys.__stdout__

        self.assertIn("nested.txt", captured.getvalue())

    def test_list_empty_directory(self):
        """Test listing an empty directory."""
        os.mkdir("emptydir")

        captured = StringIO()
        sys.stdout = captured
        handle_list(["emptydir"])
        sys.stdout = sys.__stdout__

        self.assertIn("empty directory", captured.getvalue())

    def test_list_nonexistent_directory(self):
        """Test listing a non-existent directory."""
        captured = StringIO()
        sys.stdout = captured
        handle_list(["nonexistent"])
        sys.stdout = sys.__stdout__

        self.assertIn("Directory not found", captured.getvalue())

    def test_list_file_not_directory(self):
        """Test listing a file instead of directory."""
        with open("somefile.txt", "w") as f:
            f.write("test")

        captured = StringIO()
        sys.stdout = captured
        handle_list(["somefile.txt"])
        sys.stdout = sys.__stdout__

        self.assertIn("Not a directory", captured.getvalue())

    def test_list_outside_directory(self):
        """Test security: cannot list directories outside current directory."""
        captured = StringIO()
        sys.stdout = captured
        handle_list(["/etc"])
        sys.stdout = sys.__stdout__

        self.assertIn("Access denied", captured.getvalue())


class TestHandlePwd(unittest.TestCase):
    """Test /pwd command handler."""

    def test_pwd_success(self):
        """Test /pwd shows current directory."""
        captured = StringIO()
        sys.stdout = captured
        handle_pwd([])
        sys.stdout = sys.__stdout__

        output = captured.getvalue()
        self.assertIn("Current directory", output)
        # Should contain actual current directory
        self.assertIn(os.getcwd(), output)


if __name__ == "__main__":
    unittest.main()
