"""Tests for rate limiter core engine."""


import pytest

from taolib.testing.rate_limiter.errors import RateLimitExceededError


class TestRateLimiterWhitelist:
    """Test whitelist checking."""

    def test_whitelisted_ip(self, limiter_with_rules):
        """Test IP whitelist check."""
        assert limiter_with_rules.is_whitelisted_ip("127.0.0.1") is True
        assert limiter_with_rules.is_whitelisted_ip("10.0.0.1") is True
        assert limiter_with_rules.is_whitelisted_ip("192.168.1.1") is False

    def test_whitelisted_user(self, limiter_with_rules):
        """Test user whitelist check."""
        assert limiter_with_rules.is_whitelisted_user("admin-001") is True
        assert limiter_with_rules.is_whitelisted_user("regular-user") is False

    def test_bypass_paths(self, limiter_with_rules):
        """Test bypass path check."""
        assert limiter_with_rules.is_bypass_path("/health") is True
        assert limiter_with_rules.is_bypass_path("/docs") is True
        assert limiter_with_rules.is_bypass_path("/api/test") is False


class TestRateLimiterPathRules:
    """Test path-specific rule matching."""

    def test_default_rule(self, limiter_with_rules):
        """Test default rule for unmatched paths."""
        limit, window = limiter_with_rules._get_rule_for_path("/api/test", "GET")
        assert limit == 100
        assert window == 60

    def test_specific_path_rule(self, limiter_with_rules):
        """Test specific path rule matching."""
        limit, window = limiter_with_rules._get_rule_for_path(
            "/api/v1/auth/token", "POST"
        )
        assert limit == 5
        assert window == 60

    def test_method_filtering(self, limiter_with_rules):
        """Test method-based rule filtering."""
        # GET request to auth/token should use default rule (POST only)
        limit, window = limiter_with_rules._get_rule_for_path(
            "/api/v1/auth/token", "GET"
        )
        assert limit == 100  # Default rule


class TestRateLimiterCheckLimit:
    """Test rate limit checking."""

    @pytest.mark.asyncio
    async def test_allowed_request(self, limiter):
        """Test request within limit."""
        result = await limiter.check_limit("user:test", "/api/test", "GET")
        assert result.allowed is True
        assert result.limit == 10
        assert result.remaining == 9

    @pytest.mark.asyncio
    async def test_limit_exceeded(self, limiter):
        """Test request exceeds limit."""
        # Fill up the limit
        for i in range(10):
            await limiter.record_request("user:test", "/api/test", "GET")

        # Next request should fail
        with pytest.raises(RateLimitExceededError) as exc_info:
            await limiter.check_limit("user:test", "/api/test", "GET")

        assert exc_info.value.limit == 10
        assert exc_info.value.retry_after > 0

    @pytest.mark.asyncio
    async def test_different_identifiers_independent(self, limiter):
        """Test that different identifiers have independent limits."""
        # User 1 makes 10 requests
        for i in range(10):
            await limiter.record_request("user:1", "/api/test", "GET")

        # User 2 should still have full limit
        result = await limiter.check_limit("user:2", "/api/test", "GET")
        assert result.remaining == 9


class TestRateLimiterRecord:
    """Test request recording."""

    @pytest.mark.asyncio
    async def test_record_increments_count(self, limiter):
        """Test that recording request increments count."""
        await limiter.record_request("user:test", "/api/test", "GET")
        await limiter.record_request("user:test", "/api/test", "GET")

        count = await limiter._store.get_request_count(
            "user:test", "/api/test", "GET", 60
        )
        assert count == 2



