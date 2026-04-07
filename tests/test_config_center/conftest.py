"""
Test fixtures and utilities for config_center tests.

Provides mock database connections, test data factories, and common fixtures
for unit and integration tests.
"""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Re-export shared mock classes from root tests/conftest.py so that local
# test files can still do ``from .conftest import FakeWebSocket, MockRedis``.
from conftest import (
    FakeWebSocket,  # noqa: F401
    MockCursor,  # noqa: F401
    MockMongoCollection,
    MockRedis,
    MockRedisPipeline,  # noqa: F401
    MockRedisPubSub,  # noqa: F401
)

# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_config_data() -> dict[str, Any]:
    """Return sample configuration data for testing."""
    return {
        "key": "database.host",
        "value": "localhost:5432",
        "value_type": "string",
        "environment": "development",
        "service": "auth-service",
        "tags": ["database", "connection"],
        "description": "Database host for development",
        "status": "draft",
    }


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Return sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "role_id": None,  # Will be set in tests
    }


@pytest.fixture
def sample_role_data() -> dict[str, Any]:
    """Return sample role data for testing."""
    return {
        "name": "test_editor",
        "description": "Test editor role",
        "permissions": [
            {"resource": "config", "action": "read"},
            {"resource": "config", "action": "write"},
        ],
        "allowed_environments": ["development", "testing"],
        "allowed_services": ["*"],
    }


# ---------------------------------------------------------------------------
# Mock database fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_mongo_db() -> MagicMock:
    """Create a mock MongoDB database with collections."""
    db = MagicMock()
    db.configs = MockMongoCollection("configs")
    db.config_versions = MockMongoCollection("config_versions")
    db.audit_logs = MockMongoCollection("audit_logs")
    db.users = MockMongoCollection("users")
    db.roles = MockMongoCollection("roles")
    return db


@pytest.fixture
def mock_mongo_client(mock_mongo_db: MagicMock) -> MagicMock:
    """Create a mock Motor MongoDB client."""
    client = MagicMock()
    client.get_database.return_value = mock_mongo_db
    client.admin.command = AsyncMock(return_value={"ok": 1.0})
    return client


@pytest.fixture
def mock_redis() -> MockRedis:
    """Create a mock Redis client."""
    return MockRedis()


# ---------------------------------------------------------------------------
# Authentication fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def jwt_secret() -> str:
    """Return JWT secret for testing."""
    return "test-secret-key-for-unit-tests"


@pytest.fixture
def jwt_algorithm() -> str:
    """Return JWT algorithm for testing."""
    return "HS256"


@pytest.fixture
def sample_token_payload() -> dict[str, Any]:
    """Return sample JWT token payload."""
    return {
        "sub": "test-user-id",
        "username": "testuser",
        "role": "config_admin",
        "allowed_environments": ["development", "testing"],
        "allowed_services": ["*"],
    }


# ---------------------------------------------------------------------------
# Test database cleanup
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_databases(
    mock_mongo_db: MagicMock, mock_redis: MockRedis
) -> Generator[None, Any]:
    """Automatically clean all test databases before each test."""
    # Clear mock databases
    for collection in [
        mock_mongo_db.configs,
        mock_mongo_db.config_versions,
        mock_mongo_db.audit_logs,
        mock_mongo_db.users,
        mock_mongo_db.roles,
    ]:
        collection._documents.clear()
        collection._next_id = 1

    if isinstance(mock_redis, MockRedis):
        mock_redis._data.clear()
        mock_redis._lists.clear()
        mock_redis._hashes.clear()
        mock_redis._ttl.clear()
        mock_redis._pubsub_channels.clear()

    yield
