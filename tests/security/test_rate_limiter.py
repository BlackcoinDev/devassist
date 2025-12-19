#!/usr/bin/env python3
"""
Test suite for Rate Limiter (src/security/rate_limiter.py).

Tests cover:
- Rate limiting functionality
- Request counting and window management
- Statistics tracking
"""

import pytest
import time
from src.security.rate_limiter import RateLimiter
from src.security.exceptions import RateLimitError


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_allows_below_threshold(self):
        """Test that normal request rates are allowed."""
        limiter = RateLimiter(max_calls=10, period_seconds=60)

        # Should allow requests below threshold
        for _ in range(5):
            assert limiter.check() is True

    def test_rate_limit_blocks_above_threshold(self):
        """Test that excessive request rates are blocked."""
        limiter = RateLimiter(max_calls=3, period_seconds=10)

        # Should allow up to limit
        assert limiter.check() is True
        assert limiter.check() is True
        assert limiter.check() is True

        # Should block above limit
        with pytest.raises(RateLimitError):
            limiter.check()

    def test_rate_limit_resets_after_window(self):
        """Test that rate limit resets after time window."""
        limiter = RateLimiter(max_calls=2, period_seconds=1)

        # Fill the limit
        assert limiter.check() is True
        assert limiter.check() is True
        with pytest.raises(RateLimitError):
            limiter.check()

        # Wait for window to reset
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.check() is True

    def test_rate_limit_status(self):
        """Test tracking of rate limit status."""
        limiter = RateLimiter(max_calls=5, period_seconds=60)

        # Make some requests
        for _ in range(3):
            limiter.check()

        # Get status
        status = limiter.get_status()

        assert status['calls_in_period'] == 3
        assert status['max_calls'] == 5
        assert status['remaining'] == 2
        assert status['period_seconds'] == 60

    def test_rate_limit_reset(self):
        """Test resetting the rate limiter."""
        limiter = RateLimiter(max_calls=2, period_seconds=60)
        limiter.check()
        limiter.check()

        with pytest.raises(RateLimitError):
            limiter.check()

        limiter.reset()
        assert limiter.check() is True
