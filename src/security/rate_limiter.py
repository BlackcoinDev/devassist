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
Rate limiting utilities for DevAssist.

Provides request throttling to prevent abuse, brute force attacks,
and excessive resource consumption.
"""

import threading
import time

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

    def __init__(self, max_calls: int = 10, period_seconds: int = 60):
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
