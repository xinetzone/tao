"""Tests for FastAPI dependencies."""

from unittest.mock import MagicMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from taolib.rate_limiter.dependencies import (
    get_rate_limiter,
    get_stats_service,
    get_violation_tracker,
)
from taolib.rate_limiter.limiter import RateLimiter
from taolib.rate_limiter.stats import RateLimitStatsService
from taolib.rate_limiter.violation_tracker import ViolationTracker


@pytest.fixture
def app_with_state():
    """Create a FastAPI app with mocked state objects."""
    app = FastAPI()

    # Mock state objects
    app.state.rate_limiter = MagicMock(spec=RateLimiter)
    app.state.violation_tracker = MagicMock(spec=ViolationTracker)
    app.state.rate_limit_stats_service = MagicMock(spec=RateLimitStatsService)

    return app


@pytest.fixture
def client(app_with_state):
    """Create test client."""
    return TestClient(app_with_state)


class TestGetRateLimiter:
    """Test get_rate_limiter dependency."""

    def test_get_rate_limiter(self, app_with_state):
        """Test retrieving rate limiter from app state."""

        @app_with_state.get("/test-limiter")
        async def test_endpoint(limiter: RateLimiter = Depends(get_rate_limiter)):
            return {"has_limiter": limiter is not None}

        client = TestClient(app_with_state)
        response = client.get("/test-limiter")

        assert response.status_code == 200
        assert response.json()["has_limiter"] is True

    def test_get_rate_limiter_returns_correct_instance(self, app_with_state):
        """Test that the correct rate limiter instance is returned."""
        limiter = app_with_state.state.rate_limiter

        @app_with_state.get("/test-limiter-id")
        async def test_endpoint(l: RateLimiter = Depends(get_rate_limiter)):
            return {"is_same": l is limiter}

        client = TestClient(app_with_state)
        response = client.get("/test-limiter-id")

        assert response.status_code == 200
        assert response.json()["is_same"] is True


class TestGetViolationTracker:
    """Test get_violation_tracker dependency."""

    def test_get_violation_tracker_exists(self, app_with_state):
        """Test retrieving violation tracker when it exists."""

        @app_with_state.get("/test-tracker")
        async def test_endpoint(tracker: ViolationTracker | None = Depends(get_violation_tracker)):
            return {"has_tracker": tracker is not None}

        client = TestClient(app_with_state)
        response = client.get("/test-tracker")

        assert response.status_code == 200
        assert response.json()["has_tracker"] is True

    def test_get_violation_tracker_missing(self):
        """Test retrieving violation tracker when it doesn't exist."""
        app = FastAPI()
        # Don't set violation_tracker in state
        app.state.rate_limiter = MagicMock()

        @app.get("/test-no-tracker")
        async def test_endpoint(tracker: ViolationTracker | None = Depends(get_violation_tracker)):
            return {"has_tracker": tracker is not None}

        client = TestClient(app)
        response = client.get("/test-no-tracker")

        assert response.status_code == 200
        assert response.json()["has_tracker"] is False


class TestGetStatsService:
    """Test get_stats_service dependency."""

    def test_get_stats_service(self, app_with_state):
        """Test retrieving stats service from app state."""

        @app_with_state.get("/test-stats")
        async def test_endpoint(service: RateLimitStatsService = Depends(get_stats_service)):
            return {"has_service": service is not None}

        client = TestClient(app_with_state)
        response = client.get("/test-stats")

        assert response.status_code == 200
        assert response.json()["has_service"] is True

    def test_get_stats_service_returns_correct_instance(self, app_with_state):
        """Test that the correct stats service instance is returned."""
        service = app_with_state.state.rate_limit_stats_service

        @app_with_state.get("/test-stats-id")
        async def test_endpoint(s: RateLimitStatsService = Depends(get_stats_service)):
            return {"is_same": s is service}

        client = TestClient(app_with_state)
        response = client.get("/test-stats-id")

        assert response.status_code == 200
        assert response.json()["is_same"] is True
