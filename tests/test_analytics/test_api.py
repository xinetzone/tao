"""分析模块 API 端点测试。"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from taolib.analytics.server.app import create_app


@pytest.fixture
def mock_mongo_client():
    """模拟 MongoDB 客户端。"""
    client = MagicMock()
    client.admin.command = AsyncMock(return_value={"ok": 1.0})
    return client


@pytest.fixture
def app(mock_mongo_client):
    """创建测试应用。"""
    app = create_app()
    # 手动设置 app.state 以绕过 lifespan
    app.state.mongo_client = mock_mongo_client
    app.state.db = MagicMock()
    return app


@pytest.fixture
def client(app) -> TestClient:
    """创建测试客户端。"""
    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    """测试健康检查端点。"""

    def test_health_check(self, client: TestClient, mock_mongo_client) -> None:
        mock_mongo_client.admin.command = AsyncMock(return_value={"ok": 1.0})
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


class TestDashboardEndpoint:
    """测试仪表板端点。"""

    def test_dashboard_returns_html(self, client: TestClient) -> None:
        response = client.get("/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Analytics Dashboard" in response.text


class TestSDKEndpoint:
    """测试 SDK 端点。"""

    def test_sdk_returns_javascript(self, client: TestClient) -> None:
        response = client.get("/sdk/analytics.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]
        assert "TaoAnalytics" in response.text


class TestEventsEndpoint:
    """测试事件摄入端点。"""

    def test_post_single_event(self, client: TestClient, app) -> None:
        # Mock AnalyticsService
        with patch(
            "taolib.analytics.server.api.events.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.ingest_events = AsyncMock(
                return_value={"accepted": 1, "rejected": 0}
            )
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/events",
                json={
                    "event_type": "page_view",
                    "app_id": "test-app",
                    "session_id": "sess-001",
                    "page_url": "/home",
                    "timestamp": "2026-04-06T10:00:00Z",
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data["accepted"] == 1

    def test_post_batch_events(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.events.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.ingest_events = AsyncMock(
                return_value={"accepted": 2, "rejected": 0}
            )
            mock_get.return_value = mock_service

            response = client.post(
                "/api/v1/events/batch",
                json={
                    "events": [
                        {
                            "event_type": "page_view",
                            "app_id": "test-app",
                            "session_id": "sess-001",
                            "page_url": "/home",
                            "timestamp": "2026-04-06T10:00:00Z",
                        },
                        {
                            "event_type": "click",
                            "app_id": "test-app",
                            "session_id": "sess-001",
                            "page_url": "/home",
                            "timestamp": "2026-04-06T10:01:00Z",
                            "metadata": {"element_selector": "#btn"},
                        },
                    ]
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data["accepted"] == 2

    def test_post_invalid_event(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/events",
            json={
                "event_type": "page_view",
                # missing app_id, session_id, page_url
            },
        )
        assert response.status_code == 422

    def test_post_empty_batch(self, client: TestClient) -> None:
        response = client.post(
            "/api/v1/events/batch",
            json={"events": []},
        )
        assert response.status_code == 422


class TestAPIKeyAuth:
    """测试 API Key 认证。"""

    def test_api_key_required_when_configured(self, app, mock_mongo_client) -> None:
        with patch("taolib.analytics.server.api.events.settings") as mock_settings:
            mock_settings.api_keys = ["valid-key"]
            mock_settings.max_batch_size = 1000

            client = TestClient(app, raise_server_exceptions=False)
            response = client.post(
                "/api/v1/events",
                json={
                    "event_type": "page_view",
                    "app_id": "test-app",
                    "session_id": "sess-001",
                    "page_url": "/home",
                    "timestamp": "2026-04-06T10:00:00Z",
                },
            )
            assert response.status_code == 401

    def test_api_key_accepted(self, app) -> None:
        with (
            patch("taolib.analytics.server.api.events.settings") as mock_settings,
            patch(
                "taolib.analytics.server.api.events.get_analytics_service"
            ) as mock_get,
        ):
            mock_settings.api_keys = ["valid-key"]
            mock_settings.max_batch_size = 1000
            mock_service = MagicMock()
            mock_service.ingest_events = AsyncMock(
                return_value={"accepted": 1, "rejected": 0}
            )
            mock_get.return_value = mock_service

            client = TestClient(app, raise_server_exceptions=False)
            response = client.post(
                "/api/v1/events",
                json={
                    "event_type": "page_view",
                    "app_id": "test-app",
                    "session_id": "sess-001",
                    "page_url": "/home",
                    "timestamp": "2026-04-06T10:00:00Z",
                },
                headers={"X-API-Key": "valid-key"},
            )
            assert response.status_code == 201


class TestAnalyticsEndpoints:
    """测试分析查询端点。"""

    def test_get_overview(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.analytics.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.get_overview = AsyncMock(
                return_value={
                    "total_events": 100,
                    "unique_sessions": 20,
                    "unique_users": 10,
                }
            )
            mock_get.return_value = mock_service

            response = client.get("/api/v1/analytics/overview?app_id=test-app")
            assert response.status_code == 200
            data = response.json()
            assert data["total_events"] == 100

    def test_get_funnel(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.analytics.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.get_funnel = AsyncMock(
                return_value={
                    "steps": [{"name": "/home", "count": 100, "conversion_rate": 1.0}],
                    "overall_conversion": 0.5,
                }
            )
            mock_get.return_value = mock_service

            response = client.get(
                "/api/v1/analytics/funnel?app_id=test-app&steps=/home,/signup"
            )
            assert response.status_code == 200
            data = response.json()
            assert "steps" in data
            assert "overall_conversion" in data

    def test_get_features(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.analytics.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.get_feature_ranking = AsyncMock(
                return_value={
                    "features": [{"name": "dark-mode", "count": 50}],
                }
            )
            mock_get.return_value = mock_service

            response = client.get("/api/v1/analytics/features?app_id=test-app")
            assert response.status_code == 200
            assert "features" in response.json()

    def test_get_paths(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.analytics.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.get_navigation_paths = AsyncMock(
                return_value={
                    "paths": [{"source": "/a", "target": "/b", "value": 10}],
                }
            )
            mock_get.return_value = mock_service

            response = client.get("/api/v1/analytics/paths?app_id=test-app")
            assert response.status_code == 200
            assert "paths" in response.json()

    def test_get_retention(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.analytics.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.get_retention = AsyncMock(
                return_value={
                    "sections": [{"section_id": "hero", "avg_duration_ms": 5000}],
                }
            )
            mock_get.return_value = mock_service

            response = client.get("/api/v1/analytics/retention?app_id=test-app")
            assert response.status_code == 200
            assert "sections" in response.json()

    def test_get_drop_off(self, client: TestClient) -> None:
        with patch(
            "taolib.analytics.server.api.analytics.get_analytics_service"
        ) as mock_get:
            mock_service = MagicMock()
            mock_service.get_drop_off = AsyncMock(
                return_value={
                    "steps": [
                        {
                            "name": "/cart",
                            "entered": 100,
                            "completed": 70,
                            "drop_off_rate": 0.3,
                        }
                    ],
                }
            )
            mock_get.return_value = mock_service

            response = client.get(
                "/api/v1/analytics/drop-off?app_id=test-app&steps=/cart,/checkout"
            )
            assert response.status_code == 200
            assert "steps" in response.json()

    def test_overview_missing_app_id(self, client: TestClient) -> None:
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 422

    def test_funnel_missing_steps(self, client: TestClient) -> None:
        response = client.get("/api/v1/analytics/funnel?app_id=test-app")
        assert response.status_code == 422
