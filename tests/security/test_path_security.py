#!/usr/bin/env python3
"""
Test suite for Path Security (src/security/path_security.py).

Tests cover:
- Path traversal prevention
- Path validation and sandboxing
- File read/write validation
- Directory validation
"""

import os
import pytest
from src.security.path_security import PathSecurity
from src.security.exceptions import SecurityError


class TestPathSecurity:
    """Test path security functionality."""

    def test_validate_path_success(self):
        """Test validation of safe paths."""
        current_dir = os.getcwd()
        # Relative path
        safe_path = PathSecurity.validate_path("README.md")
        assert safe_path == os.path.abspath(os.path.join(current_dir, "README.md"))

        # Another relative path
        safe_path = PathSecurity.validate_path("src/main.py")
        assert safe_path == os.path.abspath(os.path.join(current_dir, "src/main.py"))

    def test_validate_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        traversal_paths = [
            "../../etc/passwd",
            "../secret.txt",
            "/etc/passwd",
            "~/.ssh/id_rsa"
        ]

        for path in traversal_paths:
            with pytest.raises(SecurityError) as excinfo:
                PathSecurity.validate_path(path)
            assert "Path traversal attempt" in str(excinfo.value) or "Dangerous path pattern" in str(excinfo.value)

    def test_validate_file_read_limits(self):
        """Test file read validation with size limits."""
        # This assumes README.md is < 1MB
        safe_path = PathSecurity.validate_file_read("README.md")
        assert "README.md" in safe_path

    def test_validate_file_read_missing_file(self):
        """Test that missing files are rejected for read."""
        with pytest.raises(SecurityError):
            PathSecurity.validate_file_read("nonexistent_file_xyz.txt")

    def test_validate_directory_check(self):
        """Test directory validation."""
        safe_dir = PathSecurity.validate_directory("src")
        assert "src" in safe_dir

        with pytest.raises(SecurityError):
            PathSecurity.validate_directory("README.md")  # Not a directory

    def test_validate_file_write(self):
        """Test write validation."""
        safe_path = PathSecurity.validate_file_write("new_output.txt")
        assert "new_output.txt" in safe_path

    def test_dangerous_patterns(self):
        """Test that specific dangerous patterns are caught."""
        for pattern in PathSecurity.DANGEROUS_PATTERNS:
            with pytest.raises(SecurityError):
                PathSecurity.validate_path(pattern)

    def test_validate_path_with_base_dir(self):
        """Test path validation with explicit base directory."""
        base_dir = os.getcwd()  # Use current directory which exists
        safe_path = PathSecurity.validate_path("file.txt", base_dir)
        assert safe_path == os.path.abspath(os.path.join(base_dir, "file.txt"))

    def test_validate_path_absolute_path(self):
        """Test validation of absolute paths."""
        current_dir = os.getcwd()
        abs_path = os.path.abspath("README.md")
        safe_path = PathSecurity.validate_path(abs_path)
        assert safe_path == abs_path

    def test_validate_path_nested_directory(self):
        """Test validation of nested directory paths."""
        safe_path = PathSecurity.validate_path("src/core/config.py")
        assert "src/core/config.py" in safe_path
        assert os.path.exists(safe_path)

    def test_validate_path_new_file_creation(self):
        """Test validation for new file creation."""
        # This should work as long as parent directory exists
        safe_path = PathSecurity.validate_path("new_file.txt")
        assert "new_file.txt" in safe_path

    def test_validate_file_read_with_base_dir(self):
        """Test file read validation with base directory."""
        current_dir = os.getcwd()
        safe_path = PathSecurity.validate_file_read("README.md", current_dir)
        assert "README.md" in safe_path

    def test_validate_file_read_small_file(self):
        """Test file read validation with small file."""
        # Create a small test file
        test_file = "test_small.txt"
        try:
            with open(test_file, "w") as f:
                f.write("test content")

            safe_path = PathSecurity.validate_file_read(test_file)
            assert test_file in safe_path
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_validate_file_write_new_file(self):
        """Test file write validation for new file."""
        test_file = "test_new_file.txt"
        try:
            safe_path = PathSecurity.validate_file_write(test_file)
            assert test_file in safe_path
            # File shouldn't exist yet
            assert not os.path.exists(safe_path)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_validate_file_write_existing_file(self):
        """Test file write validation for existing file."""
        test_file = "test_existing.txt"
        try:
            with open(test_file, "w") as f:
                f.write("existing content")

            safe_path = PathSecurity.validate_file_write(test_file)
            assert test_file in safe_path
            assert os.path.exists(safe_path)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_validate_directory_absolute_path(self):
        """Test directory validation with absolute path."""
        current_dir = os.getcwd()
        safe_dir = PathSecurity.validate_directory(current_dir)
        assert safe_dir == os.path.abspath(current_dir)

    def test_validate_directory_relative_path(self):
        """Test directory validation with relative path."""
        safe_dir = PathSecurity.validate_directory("src")
        assert "src" in safe_dir
        assert os.path.isdir(safe_dir)


class TestPathSecurityEdgeCases:
    """Test edge cases and error paths in path security."""

    def test_validate_path_empty_string(self):
        """Test empty path raises SecurityError."""
        with pytest.raises(SecurityError) as excinfo:
            PathSecurity.validate_path("")
        assert "Empty path" in str(excinfo.value)

    def test_validate_path_invalid_type(self):
        """Test TypeError/ValueError in path construction."""
        # Use a mock to force TypeError during path construction
        from unittest.mock import patch

        with patch('os.path.abspath', side_effect=TypeError("Invalid type")):
            with pytest.raises(SecurityError) as excinfo:
                PathSecurity.validate_path("somepath")
            assert "Invalid path" in str(excinfo.value)

    def test_validate_path_parent_directory_missing(self):
        """Test parent directory doesn't exist error."""
        # Try to create a file in a non-existent nested directory
        with pytest.raises(SecurityError) as excinfo:
            PathSecurity.validate_path("nonexistent_dir/subdir/file.txt")
        assert "Parent directory doesn't exist" in str(excinfo.value)

    def test_validate_file_read_file_too_large(self):
        """Test file too large error."""
        import tempfile

        # Create a temporary large file
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            # Write more than 1MB
            f.write(b'x' * (PathSecurity.MAX_FILE_SIZE + 1))
            temp_path = f.name

        try:
            with pytest.raises(SecurityError) as excinfo:
                PathSecurity.validate_file_read(temp_path, base_dir=os.path.dirname(temp_path))
            assert "File too large" in str(excinfo.value)
        finally:
            os.remove(temp_path)

    def test_validate_file_read_os_error(self):
        """Test OSError during file size check."""
        from unittest.mock import patch

        with patch('os.path.getsize', side_effect=OSError("Permission denied")):
            with pytest.raises(SecurityError) as excinfo:
                PathSecurity.validate_file_read("README.md")
            assert "Cannot access file" in str(excinfo.value)

    def test_validate_file_read_binary_file(self):
        """Test binary file detection."""
        import tempfile

        # Create a temporary binary file in current directory
        temp_path = "temp_binary_test.bin"
        try:
            with open(temp_path, 'wb') as f:
                f.write(b'\x00\x01\x02\x03' * 256)  # Binary content with null bytes

            with pytest.raises(SecurityError) as excinfo:
                PathSecurity.validate_file_read(temp_path)
            assert "Binary file detected" in str(excinfo.value)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_validate_file_read_content_validation_error(self):
        """Test exception during file content validation."""
        from unittest.mock import patch, mock_open

        # Mock open to raise an exception
        with patch('builtins.open', side_effect=IOError("Read error")):
            with pytest.raises(SecurityError) as excinfo:
                PathSecurity.validate_file_read("README.md")
            assert "Cannot validate file content" in str(excinfo.value)

    def test_validate_file_write_to_directory(self):
        """Test cannot write to directory error."""
        with pytest.raises(SecurityError) as excinfo:
            PathSecurity.validate_file_write("src")  # src is a directory
        assert "Cannot write to directory" in str(excinfo.value)

    def test_validate_file_read_nested_security_error(self):
        """Test SecurityError propagation in nested validate_path call."""
        # Try to read a file with path traversal
        with pytest.raises(SecurityError):
            PathSecurity.validate_file_read("../../etc/passwd")
