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
