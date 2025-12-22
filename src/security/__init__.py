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
Security module for DevAssist.

This module provides comprehensive security utilities including:
- Input sanitization (SQL injection, XSS, command injection prevention)
- Path security (directory sandboxing, traversal prevention)
- Rate limiting (request throttling, abuse prevention)
- Custom security exceptions

All classes are designed to be stateless and thread-safe.
"""

from src.security.exceptions import SecurityError, DatabaseError, RateLimitError
from src.security.input_sanitizer import InputSanitizer
from src.security.path_security import PathSecurity
from src.security.rate_limiter import RateLimiter
from src.security.shell_security import ShellSecurity

__all__ = [
    "SecurityError",
    "DatabaseError",
    "RateLimitError",
    "InputSanitizer",
    "PathSecurity",
    "RateLimiter",
    "ShellSecurity",
]
