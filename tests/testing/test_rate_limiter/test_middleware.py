"""Tests for rate limit middleware."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.rate_limiter.middleware import extract_client_ip, extract_user_id


class TestClientIPExtraction:
    """Test client IP extraction from requests."""

    def test_x_forwarded_for(self):
        """Test X-Forwarded-For header."""
        request = MagicMock()
        request.headers = {
            "X-Forwarded-For": "1.2.3.4, 5.6.7.8, 9.10.11.12"
        }
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        ip = extract_client_ip(request)
        assert ip == "1.2.3.4"

    def test_x_real_ip(self):
        """Test X-Real-IP header."""
        request = MagicMock()
        request.headers = {"X-Real-IP": "10.0.0.1"}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        ip = extract_client_ip(request)
        assert ip == "10.0.0.1"

    def test_direct_connection(self):
        """Test direct connection IP."""
        request = MagicMock()
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"

        ip = extract_client_ip(request)
        assert ip == "192.168.1.1"

    def test_unknown_client(self):
        """Test when client is None."""
        request = MagicMock()
        request.headers = {}
        request.client = None

        ip = extract_client_ip(request)
        assert ip == "unknown"


class TestUserIDExtraction:
    """Test user ID extraction from requests."""

    def test_x_user_id_header(self):
        """Test X-User-ID header."""
        request = MagicMock()
        request.headers = {"X-User-ID": "user123"}

        user_id = extract_user_id(request)
        assert user_id == "user123"

    def test_no_user_id(self):
        """Test when no user ID is present."""
        request = MagicMock()
        request.headers = {}

        user_id = extract_user_id(request)
        assert user_id is None


class TestMiddlewareIntegration:
    """Test middleware integration (requires FastAPI test client)."""

    @pytest.mark.asyncio
    async def test_disabled_rate_limit(self, limiter):
        """Test that disabled limiter allows all requests."""
        limiter._config.enabled = False

        # Should not raise any exceptions
        from taolib.testing.rate_limiter.middleware import RateLimitMiddleware

        app = AsyncMock()
        middleware = RateLimitMiddleware(app, limiter)

        request = MagicMock()
        request.url.path = "/api/test"
        request.method = "GET"

        # Mock the next handler
        call_next = AsyncMock()
        response = MagicMock()
        response.headers = {}
        call_next.return_value = response

        result = await middleware.dispatch(request, call_next)
        assert result == response



