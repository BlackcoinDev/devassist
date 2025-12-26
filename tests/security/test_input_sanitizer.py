#!/usr/bin/env python3
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
Test suite for Input Sanitizer (src/security/input_sanitizer.py).

Tests cover:
- Input sanitization for dangerous characters
- SQL injection prevention
- Unicode handling
- Edge cases and error conditions
"""

import pytest
from src.security.input_sanitizer import InputSanitizer
from src.security.exceptions import SecurityError


class TestInputSanitization:
    """Test input sanitization functionality."""

    def test_sanitize_rejects_dangerous_content(self):
        """Test that dangerous patterns raise SecurityError."""
        dangerous_patterns = [
            "<script>alert('xss')</script>",
            "DROP TABLE users;",
            "SELECT * FROM users; --",
            "eval('print(\"hack\")')",
            "javascript:alert(1)",
            "../../etc/passwd",
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(SecurityError):
                InputSanitizer.sanitize_text(pattern)

    def test_sanitize_preserves_safe_input(self):
        """Test that normal text is preserved."""
        safe_inputs = [
            "Hello, this is safe text!",
            "Normal query about python",
            "User input with some (parentheses) and [brackets]",
            "Email: user@example.com",
        ]

        for safe_input in safe_inputs:
            sanitized = InputSanitizer.sanitize_text(safe_input)
            assert sanitized == safe_input

    def test_sanitize_handles_unicode(self):
        """Test Unicode character support."""
        unicode_input = "Hello 世界 🌍"
        sanitized = InputSanitizer.sanitize_text(unicode_input)

        assert sanitized == unicode_input

    def test_sanitize_handles_empty_input(self):
        """Test handling of None and empty strings."""
        assert InputSanitizer.sanitize_text("") == ""
        assert InputSanitizer.sanitize_text(None) is None

    def test_sanitize_length_limit(self):
        """Test that extremely long input is rejected."""
        long_input = "a" * 20000  # Double the limit
        with pytest.raises(SecurityError) as excinfo:
            InputSanitizer.sanitize_text(long_input)
        assert "Input too long" in str(excinfo.value)

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert InputSanitizer.sanitize_filename("test.txt") == "test.txt"
        assert InputSanitizer.sanitize_filename("../dangerous.txt") == "dangerous.txt"
        assert InputSanitizer.sanitize_filename("bad*char?.txt") == "badchar.txt"

        with pytest.raises(SecurityError):
            InputSanitizer.sanitize_filename("")

    def test_sanitize_url(self):
        """Test URL sanitization."""
        assert (
            InputSanitizer.sanitize_url("https://example.com") == "https://example.com"
        )
        assert (
            InputSanitizer.sanitize_url("http://localhost:8080/path?q=1")
            == "http://localhost:8080/path?q=1"
        )

        with pytest.raises(SecurityError):
            InputSanitizer.sanitize_url("javascript:alert(1)")

        with pytest.raises(SecurityError):
            InputSanitizer.sanitize_url("file:///etc/passwd")

        with pytest.raises(SecurityError):
            InputSanitizer.sanitize_url("not a url")
