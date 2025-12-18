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
Input sanitization utilities for DevAssist.

Provides comprehensive input validation to prevent injection attacks
and malicious content from reaching the application core.
"""

import os
import re
from urllib.parse import urlparse

from src.security.exceptions import SecurityError


class InputSanitizer:
    """
    Comprehensive input sanitization to prevent injection attacks and malicious content.

    Features:
    - SQL injection prevention
    - Command injection prevention
    - XSS prevention
    - Malicious pattern detection
    - Length validation
    - Content filtering

    All methods are class methods for stateless operation.
    """

    MAX_INPUT_LENGTH = 10000  # 10KB limit

    DANGEROUS_PATTERNS = [
        # SQL injection patterns
        r";\s*",
        r"--",
        r"\/\*",
        r"\*\/",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"INSERT\s+INTO",
        r"UPDATE\s+.*SET",
        r"UNION\s+SELECT",
        # Command injection patterns
        r"&&",
        r"\|\|",
        r";",
        r"\$\(",
        r"`",
        r"\.\./",
        r"<\(script\)",
        r"javascript:",
        # XSS patterns
        r"<script>",
        r"onerror=",
        r"onload=",
        r"javascript:",
        r"vbscript:",
        r"expression\(",
        # Malicious content
        r"__import__",
        r"eval\(",
        r"exec\(",
        r"compile\(",
        r"pickle\.load",
        r"subprocess\.",
        r"os\.system",
    ]

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Sanitize text input to prevent injection attacks.

        Args:
            text: Input text to sanitize

        Returns:
            str: Sanitized text

        Raises:
            SecurityError: If malicious content is detected
        """
        if not text:
            return text

        # Check length
        if len(text) > cls.MAX_INPUT_LENGTH:
            raise SecurityError(
                f"Input too long: {len(text)} characters (max {cls.MAX_INPUT_LENGTH})"
            )

        # Check for dangerous patterns
        text_lower = text.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower):
                raise SecurityError(f"Dangerous content detected: {pattern}")

        # Normalize whitespace
        text = " ".join(text.split())

        # Remove excessive special characters
        text = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", text)  # Remove control characters

        return text

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and invalid characters.

        Args:
            filename: Filename to sanitize

        Returns:
            str: Sanitized filename

        Raises:
            SecurityError: If filename is invalid
        """
        if not filename:
            raise SecurityError("Empty filename")

        # Remove path components
        filename = os.path.basename(filename)

        # Remove dangerous characters
        safe_chars = (
            "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )
        safe_filename = "".join(c for c in filename if c in safe_chars)

        if not safe_filename:
            raise SecurityError("Invalid filename characters")

        # Check length
        if len(safe_filename) > 255:
            raise SecurityError("Filename too long")

        return safe_filename

    @classmethod
    def sanitize_url(cls, url: str) -> str:
        """
        Sanitize URL input to prevent malicious URLs.

        Args:
            url: URL to sanitize

        Returns:
            str: Sanitized URL

        Raises:
            SecurityError: If URL is malicious
        """
        if not url:
            raise SecurityError("Empty URL")

        # Check for dangerous protocols
        dangerous_protocols = ["javascript:", "data:", "vbscript:", "file:"]
        url_lower = url.lower()
        for protocol in dangerous_protocols:
            if url_lower.startswith(protocol):
                raise SecurityError(f"Dangerous URL protocol: {protocol}")

        # Validate URL structure
        try:
            result = urlparse(url)
            if not result.scheme or not result.netloc:
                raise SecurityError("Invalid URL structure")
        except Exception as e:
            raise SecurityError(f"Invalid URL: {e}")

        return url
