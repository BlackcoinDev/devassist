#!/usr/bin/env python3
"""
Test suite for Input Sanitizer (src/security/input_sanitizer.py).

Tests cover:
- Input sanitization for dangerous characters
- SQL injection prevention
- Unicode handling
- Edge cases and error conditions
"""

import pytest
from src.security.input_sanitizer import sanitize_input, detect_sql_injection


class TestInputSanitization:
    """Test input sanitization functionality."""

    def test_sanitize_removes_dangerous_chars(self):
        """Test removal of dangerous characters like <, >, &, etc."""
        dangerous_input = "<script>alert('xss')</script>&malicious"
        sanitized = sanitize_input(dangerous_input)
        
        assert "<script>" not in sanitized
        assert "</script>" not in sanitized
        assert "&" not in sanitized

    def test_sanitize_preserves_safe_input(self):
        """Test that normal text is preserved."""
        safe_input = "Hello, this is safe text!"
        sanitized = sanitize_input(safe_input)
        
        assert sanitized == safe_input

    def test_sanitize_handles_unicode(self):
        """Test Unicode character support."""
        unicode_input = "Hello 世界 🌍"
        sanitized = sanitize_input(unicode_input)
        
        assert sanitized == unicode_input

    def test_sanitize_empty_input(self):
        """Test handling of empty strings."""
        empty_input = ""
        sanitized = sanitize_input(empty_input)
        
        assert sanitized == ""

    def test_sanitize_long_input(self):
        """Test handling of large inputs."""
        long_input = "a" * 10000
        sanitized = sanitize_input(long_input)
        
        assert len(sanitized) == 10000


class TestSQLInjectionPrevention:
    """Test SQL injection detection and prevention."""

    def test_detect_sql_injection(self):
        """Test detection of SQL injection keywords."""
        sql_injection = "SELECT * FROM users WHERE '1'='1'"
        is_sql = detect_sql_injection(sql_injection)
        
        assert is_sql is True

    def test_sanitize_sql_input(self):
        """Test sanitization of SQL-dangerous input."""
        sql_input = "DROP TABLE users;--"
        sanitized = sanitize_input(sql_input)
        
        # Should remove or escape dangerous SQL
        assert "DROP TABLE" not in sanitized
        assert "--" not in sanitized

    def test_parameterized_query_support(self):
        """Test that parameterized queries are safe."""
        safe_query = "SELECT * FROM users WHERE id = ?"
        is_sql = detect_sql_injection(safe_query)
        
        # Parameterized queries should be considered safe
        assert is_sql is False

    def test_detect_union_attack(self):
        """Test detection of UNION attacks."""
        union_attack = "' UNION SELECT username, password FROM users--"
        is_sql = detect_sql_injection(union_attack)
        
        assert is_sql is True

    def test_detect_comment_attack(self):
        """Test detection of SQL comment attacks."""
        comment_attack = "admin'-- comment"
        is_sql = detect_sql_injection(comment_attack)
        
        assert is_sql is True