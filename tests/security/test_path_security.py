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
            PathSecurity.validate_directory("README.md") # Not a directory

    def test_validate_file_write(self):
        """Test write validation."""
        safe_path = PathSecurity.validate_file_write("new_output.txt")
        assert "new_output.txt" in safe_path

    def test_dangerous_patterns(self):
        """Test that specific dangerous patterns are caught."""
        for pattern in PathSecurity.DANGEROUS_PATTERNS:
            with pytest.raises(SecurityError):
                PathSecurity.validate_path(pattern)