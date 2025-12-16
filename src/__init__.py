"""
DevAssist - AI-powered learning assistant and development tool.

This package provides the core functionality for the DevAssist application,
including CLI and GUI interfaces, AI tools, and knowledge management.
"""

# Re-export security module for backwards compatibility
from src.security import (
    SecurityError,
    DatabaseError,
    RateLimitError,
    InputSanitizer,
    PathSecurity,
    RateLimiter,
)

__all__ = [
    "SecurityError",
    "DatabaseError",
    "RateLimitError",
    "InputSanitizer",
    "PathSecurity",
    "RateLimiter",
]
