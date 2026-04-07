"""Config Center API 端点集成测试。

测试配置 CRUD、版本管理和回滚 API 端点。
使用 MockMongoCollection 和 InMemoryConfigCache 替代真实数据库。
"""

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

# Ensure src/ is in sys.path
_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from taolib.config_center.cache.config_cache import InMemoryConfigCache
from taolib.config_center.models.user import UserDocument
from taolib.config_center.repository.audit_repo import AuditLogRepository
from taolib.config_center.repository.config_repo import ConfigRepository
from taolib.config_center.repository.version_repo import VersionRepository
from taolib.config_center.server.api.router import api_router
from taolib.config_center.server.dependencies import (
    get_audit_repo,
    get_cache,
    get_config_repo,
    get_current_user,
    get_version_repo,
)

MOCK_USER = UserDocument(
    _id="test-user-id",
    username="testuser",
    email="test@example.com",
    password_hash="hashed_password",
    role_ids=["admin"],
)


@pytest.fixture
def test_app(mock_mongo_db):
    """Create a test FastAPI app with mock dependencies."""
    app = FastAPI()
    app.include_router(api_router)

    cache = InMemoryConfigCache()

    config_repo = ConfigRepository(mock_mongo_db.configs)
    version_repo = VersionRepository(mock_mongo_db.config_versions)
    audit_repo = AuditLogRepository(mock_mongo_db.audit_logs)

    app.dependency_overrides[get_config_repo] = lambda: config_repo
    app.dependency_overrides[get_version_repo] = lambda: version_repo
    app.dependency_overrides[get_audit_repo] = lambda: audit_repo
    app.dependency_overrides[get_cache] = lambda: cache
    app.dependency_overrides[get_current_user] = lambda: MOCK_USER

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Create a test HTTP client."""
    return TestClient(test_app)


def _config_payload(**overrides):
    """Helper to build a config creation payload."""
    data = {
        "key": "database.host",
        "environment": "development",
        "service": "auth-service",
        "value": "localhost:5432",
        "value_type": "string",
        "description": "Database host",
        "tags": ["database"],
        "status": "draft",
    }
    data.update(overrides)
    return data


# ---------------------------------------------------------------------------
# Config CRUD tests
# ---------------------------------------------------------------------------


class TestConfigCRUD:
    """配置 CRUD 端点测试。"""

    def test_create_config(self, client):
        """测试创建配置。"""
        resp = client.post("/api/v1/configs", json=_config_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["key"] == "database.host"
        assert body["environment"] == "development"
        assert body["service"] == "auth-service"
        assert body["value"] == "localhost:5432"
        assert body["version"] == 1
        assert body["created_by"] == "test-user-id"
        assert "id" in body

    def test_get_config(self, client):
        """测试获取配置详情。"""
        create_resp = client.post("/api/v1/configs", json=_config_payload())
        config_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/configs/{config_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == config_id
        assert body["key"] == "database.host"

    def test_get_config_not_found(self, client):
        """测试获取不存在的配置返回 404。"""
        resp = client.get("/api/v1/configs/nonexistent-id")
        assert resp.status_code == 404

    def test_update_config(self, client):
        """测试更新配置。"""
        create_resp = client.post("/api/v1/configs", json=_config_payload())
        config_id = create_resp.json()["id"]

        resp = client.put(
            f"/api/v1/configs/{config_id}",
            json={"value": "new-host:5433"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["value"] == "new-host:5433"
        assert body["version"] == 2

    def test_update_config_not_found(self, client):
        """测试更新不存在的配置返回 404。"""
        resp = client.put(
            "/api/v1/configs/nonexistent-id",
            json={"value": "new-value"},
        )
        assert resp.status_code == 404

    def test_delete_config(self, client):
        """测试删除配置。"""
        create_resp = client.post("/api/v1/configs", json=_config_payload())
        config_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/configs/{config_id}")
        assert resp.status_code == 204

        # Verify deleted
        get_resp = client.get(f"/api/v1/configs/{config_id}")
        assert get_resp.status_code == 404

    def test_delete_config_not_found(self, client):
        """测试删除不存在的配置返回 404。"""
        resp = client.delete("/api/v1/configs/nonexistent-id")
        assert resp.status_code == 404

    def test_list_configs(self, client):
        """测试查询配置列表。"""
        # Create two configs
        client.post("/api/v1/configs", json=_config_payload())
        client.post(
            "/api/v1/configs",
            json=_config_payload(key="database.port", value="5432"),
        )

        resp = client.get("/api/v1/configs")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2

    def test_publish_config(self, client):
        """测试发布配置（draft → active）。"""
        create_resp = client.post("/api/v1/configs", json=_config_payload())
        config_id = create_resp.json()["id"]

        resp = client.post(f"/api/v1/configs/{config_id}/publish")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "active"


# ---------------------------------------------------------------------------
# Version endpoint tests
# ---------------------------------------------------------------------------


class TestVersionEndpoints:
    """版本管理端点测试。"""

    def _create_config(self, client) -> str:
        """辅助方法：创建配置并返回 config_id。"""
        resp = client.post("/api/v1/configs", json=_config_payload())
        return resp.json()["id"]

    def test_list_versions(self, client):
        """测试获取版本历史。"""
        config_id = self._create_config(client)

        resp = client.get(f"/api/v1/configs/{config_id}/versions")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) >= 1
        assert body[0]["config_id"] == config_id
        assert body[0]["version"] == 1
        assert body[0]["change_type"] == "create"

    def test_list_versions_after_update(self, client):
        """测试更新后版本历史包含两条记录。"""
        config_id = self._create_config(client)

        # Update config to create version 2
        client.put(
            f"/api/v1/configs/{config_id}",
            json={"value": "updated-host"},
        )

        resp = client.get(f"/api/v1/configs/{config_id}/versions")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        # Versions are returned in descending order
        assert body[0]["version"] == 2
        assert body[1]["version"] == 1

    def test_get_version(self, client):
        """测试获取指定版本详情。"""
        config_id = self._create_config(client)

        resp = client.get(f"/api/v1/configs/{config_id}/versions/1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["version"] == 1
        assert body["value"] == "localhost:5432"
        assert body["change_type"] == "create"

    def test_get_version_not_found(self, client):
        """测试获取不存在版本返回 404。"""
        config_id = self._create_config(client)

        resp = client.get(f"/api/v1/configs/{config_id}/versions/999")
        assert resp.status_code == 404

    def test_rollback_to_version(self, client):
        """测试回滚到指定版本。"""
        config_id = self._create_config(client)

        # Update to version 2
        client.put(
            f"/api/v1/configs/{config_id}",
            json={"value": "new-host:9999"},
        )

        # Verify current value is updated
        get_resp = client.get(f"/api/v1/configs/{config_id}")
        assert get_resp.json()["value"] == "new-host:9999"
        assert get_resp.json()["version"] == 2

        # Rollback to version 1
        resp = client.post(
            f"/api/v1/configs/{config_id}/versions/1/rollback"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "已回滚到版本 1"
        assert body["config_id"] == config_id
        assert body["new_version"] == 3

        # Verify config value restored
        get_resp = client.get(f"/api/v1/configs/{config_id}")
        assert get_resp.json()["value"] == "localhost:5432"
        assert get_resp.json()["version"] == 3

    def test_rollback_config_not_found(self, client):
        """测试回滚不存在的配置返回 404。"""
        resp = client.post(
            "/api/v1/configs/nonexistent-id/versions/1/rollback"
        )
        assert resp.status_code == 404

    def test_rollback_version_not_found(self, client):
        """测试回滚到不存在的版本返回 404。"""
        config_id = self._create_config(client)

        resp = client.post(
            f"/api/v1/configs/{config_id}/versions/999/rollback"
        )
        assert resp.status_code == 404

    def test_rollback_creates_version_record(self, client):
        """测试回滚后创建了新的版本记录。"""
        config_id = self._create_config(client)

        # Update to v2
        client.put(
            f"/api/v1/configs/{config_id}",
            json={"value": "changed-value"},
        )

        # Rollback to v1
        client.post(f"/api/v1/configs/{config_id}/versions/1/rollback")

        # Check version history: should have 3 versions
        resp = client.get(f"/api/v1/configs/{config_id}/versions")
        body = resp.json()
        assert len(body) == 3

        # Latest version (v3) should be rollback type
        rollback_version = next(v for v in body if v["version"] == 3)
        assert rollback_version["change_type"] == "rollback"
        assert rollback_version["value"] == "localhost:5432"

    def test_compare_versions(self, client):
        """测试版本差异比较。"""
        config_id = self._create_config(client)

        # Update to v2
        client.put(
            f"/api/v1/configs/{config_id}",
            json={"value": "new-host:5433"},
        )

        resp = client.get(
            f"/api/v1/configs/{config_id}/versions/diff/1/to/2"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["config_id"] == config_id
        assert body["v1"]["version"] == 1
        assert body["v1"]["value"] == "localhost:5432"
        assert body["v2"]["version"] == 2
        assert body["v2"]["value"] == "new-host:5433"
        assert body["changed"] is True

    def test_compare_identical_versions(self, client):
        """测试比较相同版本返回未变更。"""
        config_id = self._create_config(client)

        resp = client.get(
            f"/api/v1/configs/{config_id}/versions/diff/1/to/1"
        )
        assert resp.status_code == 200
        assert resp.json()["changed"] is False
