"""Tests for rate limiter API routes."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from taolib.testing.rate_limiter.api.router import router
from taolib.testing.rate_limiter.models import RealtimeStats, TopUserEntry, ViolationStatsEntry
from taolib.testing.rate_limiter.stats import RateLimitStatsService


@pytest.fixture
def mock_stats_service():
    """Create a mock stats service."""
    service = AsyncMock(spec=RateLimitStatsService)
    service.get_top_users.return_value = [
        TopUserEntry(identifier="user:123", request_count=150, identifier_type="user"),
        TopUserEntry(identifier="ip:1.2.3.4", request_count=80, identifier_type="ip"),
    ]
    service.get_violation_stats.return_value = [
        ViolationStatsEntry(
            identifier="user:456",
            count=25,
            identifier_type="user",
            last_violation=datetime.now(UTC),
        )
    ]
    service.get_realtime.return_value = RealtimeStats(
        active_requests=42,
        requests_per_second=0.7,
        top_paths=[
            {"path": "/api/test", "count": 30},
            {"path": "/api/heavy", "count": 12},
        ],
    )
    return service


@pytest.fixture
def app(mock_stats_service):
    """Create a FastAPI test application with mocked dependencies."""
    app = FastAPI()

    # Mock the app state
    app.state.rate_limit_stats_service = mock_stats_service

    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestTopUsersEndpoint:
    """Test /stats/top-users endpoint."""

    def test_get_top_users_default_params(self, client, mock_stats_service):
        """Test top users with default parameters."""
        response = client.get("/stats/top-users")

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) == 2
        assert data["users"][0]["identifier"] == "user:123"
        assert data["users"][0]["request_count"] == 150

        mock_stats_service.get_top_users.assert_called_once_with(20)

    def test_get_top_users_custom_params(self, client, mock_stats_service):
        """Test top users with custom parameters."""
        response = client.get("/stats/top-users?period_hours=48&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 2

        mock_stats_service.get_top_users.assert_called_once_with(10)

    def test_get_top_users_empty(self, client, mock_stats_service):
        """Test top users with no data."""
        mock_stats_service.get_top_users.return_value = []

        response = client.get("/stats/top-users")

        assert response.status_code == 200
        data = response.json()
        assert data["users"] == []


class TestViolationsEndpoint:
    """Test /stats/violations endpoint."""

    def test_get_violations_default_params(self, client, mock_stats_service):
        """Test violations with default parameters."""
        response = client.get("/stats/violations")

        assert response.status_code == 200
        data = response.json()
        assert "violations" in data
        assert len(data["violations"]) == 1
        assert data["violations"][0]["identifier"] == "user:456"
        assert data["violations"][0]["count"] == 25

        mock_stats_service.get_violation_stats.assert_called_once_with(24)

    def test_get_violations_custom_params(self, client, mock_stats_service):
        """Test violations with custom parameters."""
        response = client.get("/stats/violations?period_hours=12")

        assert response.status_code == 200

        mock_stats_service.get_violation_stats.assert_called_once_with(12)

    def test_get_violations_empty(self, client, mock_stats_service):
        """Test violations with no data."""
        mock_stats_service.get_violation_stats.return_value = []

        response = client.get("/stats/violations")

        assert response.status_code == 200
        data = response.json()
        assert data["violations"] == []


class TestRealtimeEndpoint:
    """Test /stats/realtime endpoint."""

    def test_get_realtime_default_params(self, client, mock_stats_service):
        """Test realtime stats with default parameters."""
        response = client.get("/stats/realtime")

        assert response.status_code == 200
        data = response.json()
        assert data["active_requests"] == 42
        assert data["requests_per_second"] == 0.7
        assert len(data["top_paths"]) == 2

        mock_stats_service.get_realtime.assert_called_once_with(60)

    def test_get_realtime_custom_params(self, client, mock_stats_service):
        """Test realtime stats with custom parameters."""
        response = client.get("/stats/realtime?window_seconds=120")

        assert response.status_code == 200

        mock_stats_service.get_realtime.assert_called_once_with(120)



