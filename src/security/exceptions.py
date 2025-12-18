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
Security-related exceptions for DevAssist.

These exceptions provide clear error types for different security scenarios,
enabling proper error handling and user feedback.
"""


class SecurityError(Exception):
    """
    Custom exception for security-related errors.

    Raised when:
    - Malicious content is detected in user input
    - Path traversal attempts are blocked
    - URL validation fails
    - Other security policy violations occur
    """

    pass


class DatabaseError(Exception):
    """
    Custom exception for database-related errors.

    Raised when:
    - Database connection is not initialized
    - SQL query execution fails
    - Transaction commits fail
    """

    pass


class RateLimitError(Exception):
    """
    Custom exception for rate limiting violations.

    Raised when:
    - Request frequency exceeds configured limits
    - Retry should be attempted after a cooldown period
    """

    pass
