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
Rate limiting utilities for DevAssist.

Provides request throttling to prevent abuse, brute force attacks,
and excessive resource consumption.
"""

import threading
import time
from typing import Dict, Optional

from src.security.exceptions import RateLimitError


class RateLimiter:
    """
    Rate limiting to prevent abuse and brute force attacks.

    Features:
    - Request frequency tracking
    - Exponential backoff
    - Multiple limiter instances
    - Thread-safe operations

    Each instance tracks its own call history, allowing different
    rate limits for different operations.
    """

    def __init__(self, max_calls: int = 10, period_seconds: float = 60.0):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the period
            period_seconds: Time period for rate limiting (in seconds)
        """
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls: list[float] = []
        self.lock = threading.Lock()

    def check(self) -> bool:
        """
        Check if operation is allowed under rate limits.

        Returns:
            bool: True if operation is allowed

        Raises:
            RateLimitError: If rate limit exceeded
        """
        with self.lock:
            now = time.time()
            # Remove old calls outside the period window
            self.calls = [t for t in self.calls if now - t < self.period]

            if len(self.calls) >= self.max_calls:
                oldest_call = min(self.calls)
                wait_time = self.period - (now - oldest_call)
                raise RateLimitError(
                    f"Rate limit exceeded. Try again in {wait_time:.1f} seconds"
                )

            # Add current call
            self.calls.append(now)
            return True

    def get_status(self) -> dict:
        """
        Get current rate limit status.

        Returns:
            dict: Status information including:
                - calls_in_period: Number of calls made in current period
                - max_calls: Maximum allowed calls
                - period_seconds: Length of the rate limit period
                - remaining: Number of calls still available
        """
        with self.lock:
            now = time.time()
            recent_calls = [t for t in self.calls if now - t < self.period]
            return {
                "calls_in_period": len(recent_calls),
                "max_calls": self.max_calls,
                "period_seconds": self.period,
                "remaining": self.max_calls - len(recent_calls),
            }

    def reset(self) -> None:
        """Reset the rate limiter, clearing all tracked calls."""
        with self.lock:
            self.calls.clear()


class RateLimitManager:
    """
    Central manager for tool rate limiting.

    Maintains a registry of RateLimiter instances for different tools
    and enforces limits defined in constants.py.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(RateLimitManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the manager."""
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = threading.Lock()

    @classmethod
    def check_limit(cls, tool_name: str) -> bool:
        """
        Check if a tool execution is allowed.

        Args:
            tool_name: Name of the tool being executed

        Returns:
            True if allowed

        Raises:
            RateLimitError: If limit exceeded
        """
        manager = cls()
        return manager._check(tool_name)

    def _check(self, tool_name: str) -> bool:
        """Internal check implementation."""
        from src.core.constants import RATE_LIMITS

        with self.lock:
            if tool_name not in self.limiters:
                # Determine limit config
                # Check for exact match or prefix match (e.g., git_status -> git)
                limit_config = RATE_LIMITS.get("default", (60, 60))

                # Exact match
                if tool_name in RATE_LIMITS:
                    limit_config = RATE_LIMITS[tool_name]
                else:
                    # Prefix match
                    for key, config in RATE_LIMITS.items():
                        if tool_name.startswith(key + "_") or tool_name.startswith(key):
                            limit_config = config
                            break

                self.limiters[tool_name] = RateLimiter(
                    max_calls=limit_config[0], period_seconds=limit_config[1]
                )

            limiter = self.limiters[tool_name]

        return limiter.check()

    @classmethod
    def get_status(cls, tool_name: str) -> Optional[dict]:
        """Get status for a specific tool."""
        manager = cls()
        with manager.lock:
            if tool_name in manager.limiters:
                return manager.limiters[tool_name].get_status()
        return None

    @classmethod
    def reset_all(cls) -> None:
        """Reset all limiters (useful for testing)."""
        manager = cls()
        with manager.lock:
            manager.limiters.clear()
