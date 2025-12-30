#!/usr/bin/env python3
"""
Test suite for Rate Limiting.
"""

import time
import pytest
from src.security.rate_limiter import RateLimiter, RateLimitManager
from src.security.exceptions import RateLimitError


class TestRateLimiter:
    """Test individual RateLimiter behavior."""

    def test_rate_limiter_allows_under_limit(self):
        """Test that calls under the limit are allowed."""
        limiter = RateLimiter(max_calls=5, period_seconds=60)
        for _ in range(5):
            assert limiter.check() is True

    def test_rate_limiter_blocks_over_limit(self):
        """Test that calls over the limit are blocked."""
        limiter = RateLimiter(max_calls=2, period_seconds=60)
        assert limiter.check() is True
        assert limiter.check() is True

        with pytest.raises(RateLimitError):
            limiter.check()

    def test_rate_limiter_resets_after_period(self):
        """Test that limits reset after the period expires."""
        limiter = RateLimiter(max_calls=1, period_seconds=0.1)
        assert limiter.check() is True

        with pytest.raises(RateLimitError):
            limiter.check()

        time.sleep(0.15)
        # Should be allowed again
        assert limiter.check() is True


class TestRateLimitManager:
    """Test the central RateLimitManager."""

    def setup_method(self):
        """Reset manager state."""
        RateLimitManager.reset_all()

    def teardown_method(self):
        """Reset manager state."""
        RateLimitManager.reset_all()

    def test_check_limit_creates_limiter(self):
        """Test that checking a limit creates a new limiter instance."""
        assert RateLimitManager.get_status("test_tool") is None

        # Should initialize with default limits (60, 60)
        allowed = RateLimitManager.check_limit("test_tool")
        assert allowed is True

        status = RateLimitManager.get_status("test_tool")
        assert status is not None
        assert status["max_calls"] == 60

    def test_check_limit_uses_constants(self):
        """Test that manager uses constants for limits."""
        # shell is defined as (10, 60) in constants.py

        # We need to make sure we are using the actual constants or mocking them
        # Since we imported the module code which imports constants, let's trust integration
        # or verify the specific limit.

        RateLimitManager.check_limit("shell")
        status = RateLimitManager.get_status("shell")
        assert status["max_calls"] == 10

    def test_check_limit_prefix_matching(self):
        """Test that prefix matching works (git_status -> git limit)."""
        # git is (20, 60)

        RateLimitManager.check_limit("git_status")
        status = RateLimitManager.get_status("git_status")
        assert status["max_calls"] == 20

    def test_check_limit_raises_error(self):
        """Test that manager raises error when limit exceeded."""

        # Harder to patch local import constant.
        # Instead, we force a limiter into the manager manually
        manager = RateLimitManager()
        with manager.lock:
            # Inject a restrictive limiter directly
            manager.limiters["forced"] = RateLimiter(max_calls=1, period_seconds=60)

        assert RateLimitManager.check_limit("forced") is True

        with pytest.raises(RateLimitError):
            RateLimitManager.check_limit("forced")
