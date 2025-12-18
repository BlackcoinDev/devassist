#!/usr/bin/env python3
"""
Test suite for Rate Limiter (src/security/rate_limiter.py).

Tests cover:
- Rate limiting functionality
- Request counting and window management
- Per-user rate limiting
- Statistics tracking
"""

import pytest
import time
from src.security.rate_limiter import RateLimiter


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limit_allows_below_threshold(self):
        """Test that normal request rates are allowed."""
        limiter = RateLimiter(limit=10, window=60)
        
        # Should allow requests below threshold
        for i in range(5):
            assert limiter.allow_request("user1") is True

    def test_rate_limit_blocks_above_threshold(self):
        """Test that excessive request rates are blocked."""
        limiter = RateLimiter(limit=3, window=1)
        
        # Should allow up to limit
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        
        # Should block above limit
        assert limiter.allow_request("user1") is False

    def test_rate_limit_resets_after_window(self):
        """Test that rate limit resets after time window."""
        limiter = RateLimiter(limit=2, window=1)
        
        # Fill the limit
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is False  # Blocked
        
        # Wait for window to reset
        time.sleep(1.1)
        
        # Should be allowed again
        assert limiter.allow_request("user1") is True

    def test_rate_limit_per_user(self):
        """Test that rate limits are applied per user."""
        limiter = RateLimiter(limit=2, window=60)
        
        # User1 hits limit
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is True
        assert limiter.allow_request("user1") is False
        
        # User2 should still be allowed
        assert limiter.allow_request("user2") is True
        assert limiter.allow_request("user2") is True

    def test_rate_limit_statistics(self):
        """Test tracking of rate limit statistics."""
        limiter = RateLimiter(limit=5, window=60)
        
        # Make some requests
        for i in range(3):
            limiter.allow_request("user1")
        
        # Get statistics
        stats = limiter.get_statistics()
        
        assert 'total_requests' in stats
        assert 'blocked_requests' in stats
        assert 'active_users' in stats