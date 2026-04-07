"""Tests for rate limiter store."""

import time

import pytest

from taolib.rate_limiter.store import InMemoryRateLimitStore


class TestInMemoryRateLimitStore:
    """Test in-memory store implementation."""

    @pytest.mark.asyncio
    async def test_record_and_count(self):
        """Test recording requests and getting count."""
        store = InMemoryRateLimitStore()
        identifier = "user:test123"
        path = "/api/test"
        method = "GET"
        now = time.time()

        count = await store.record_request(identifier, path, method, now, 60)
        assert count == 1

        count = await store.record_request(identifier, path, method, now + 1, 60)
        assert count == 2

    @pytest.mark.asyncio
    async def test_window_expiry(self):
        """Test that expired requests are cleaned up."""
        store = InMemoryRateLimitStore()
        identifier = "user:test123"
        path = "/api/test"
        method = "GET"

        # Record request 60 seconds ago
        old_time = time.time() - 120
        await store.record_request(identifier, path, method, old_time, 60)

        # Current count should be 0 (expired)
        count = await store.get_request_count(identifier, path, method, 60)
        assert count == 0

    @pytest.mark.asyncio
    async def test_get_oldest_in_window(self):
        """Test getting oldest request in window."""
        store = InMemoryRateLimitStore()
        identifier = "user:test123"
        path = "/api/test"
        method = "GET"
        now = time.time()

        await store.record_request(identifier, path, method, now - 10, 60)
        await store.record_request(identifier, path, method, now, 60)

        oldest = await store.get_oldest_in_window(identifier, path, method, 60)
        assert oldest is not None
        assert oldest <= now - 9  # Approximately 10 seconds ago

    @pytest.mark.asyncio
    async def test_increment_stats(self):
        """Test stats increment."""
        store = InMemoryRateLimitStore()

        await store.increment_stats("user:test", "/api/test")
        await store.increment_stats("user:test", "/api/test")
        await store.increment_stats("user:other", "/api/other")

        top_users = await store.get_top_users()
        assert len(top_users) == 2
        assert top_users[0] == ("user:test", 2)

    @pytest.mark.asyncio
    async def test_realtime_requests(self):
        """Test realtime request statistics."""
        store = InMemoryRateLimitStore()

        # Record some requests
        now = time.time()
        for i in range(5):
            store._realtime.append((now - i, "/api/test"))
        for i in range(3):
            store._realtime.append((now - i, "/api/other"))

        stats = await store.get_realtime_requests(60)
        assert stats["active_requests"] == 8
        assert len(stats["top_paths"]) == 2
        assert stats["top_paths"][0]["path"] == "/api/test"
        assert stats["top_paths"][0]["count"] == 5


class TestRedisKeyGeneration:
    """Test Redis key generation functions."""

    def test_make_window_key(self):
        """Test window key generation."""
        from taolib.rate_limiter.keys import make_window_key

        key = make_window_key("user:123", "/api/test", "GET")
        assert key == "ratelimit:window:user:123:/api/test:GET"

    def test_make_window_key_normalization(self):
        """Test key normalization."""
        from taolib.rate_limiter.keys import make_window_key

        key1 = make_window_key("user:123", "/api/test/", "get")
        key2 = make_window_key("user:123", "/api/test", "GET")
        assert key1 == key2

    def test_parse_identifier_type(self):
        """Test identifier type parsing."""
        from taolib.rate_limiter.keys import parse_identifier_type

        assert parse_identifier_type("user:123") == "user"
        assert parse_identifier_type("ip:192.168.1.1") == "ip"
        assert parse_identifier_type("unknown") == "unknown"
