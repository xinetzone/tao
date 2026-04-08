"""Shared fixtures for rate limiter tests."""

import pytest

from taolib.testing.rate_limiter.config import RateLimitConfig
from taolib.testing.rate_limiter.limiter import RateLimiter
from taolib.testing.rate_limiter.store import InMemoryRateLimitStore


@pytest.fixture
def config():
    """Default rate limit configuration."""
    return RateLimitConfig(
        enabled=True,
        default_limit=10,
        window_seconds=60,
    )


@pytest.fixture
def config_with_path_rules():
    """Configuration with path-specific rules."""
    from taolib.testing.rate_limiter.models import PathRule, WhitelistConfig

    return RateLimitConfig(
        enabled=True,
        default_limit=100,
        window_seconds=60,
        path_rules={
            "/api/v1/auth/token": PathRule(
                limit=5,
                window_seconds=60,
                methods=["POST"],
            ),
            "/api/v1/audit": PathRule(
                limit=30,
                window_seconds=60,
                methods=["GET"],
            ),
        },
        whitelist=WhitelistConfig(
            ips=["127.0.0.1", "10.0.0.0/8"],
            user_ids=["admin-001"],
            bypass_paths=["/health", "/docs"],
        ),
    )


@pytest.fixture
def store():
    """In-memory store for testing."""
    return InMemoryRateLimitStore()


@pytest.fixture
def limiter(config, store):
    """Rate limiter instance with in-memory store."""
    return RateLimiter(config=config, store=store)


@pytest.fixture
def limiter_with_rules(config_with_path_rules, store):
    """Rate limiter with path rules and whitelist."""
    return RateLimiter(config=config_with_path_rules, store=store)



