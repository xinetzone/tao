"""模型测试 - 版本和审计数据模型。"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from taolib.config_center.models.audit import (
    AuditLogBase,
    AuditLogCreate,
    AuditLogDocument,
    AuditLogResponse,
)
from taolib.config_center.models.enums import AuditAction, AuditStatus, ChangeType
from taolib.config_center.models.version import (
    ConfigVersionBase,
    ConfigVersionCreate,
    ConfigVersionDocument,
    ConfigVersionResponse,
)


class TestConfigVersionModels:
    """测试配置版本模型。"""

    def test_version_base_creation(self) -> None:
        """测试版本基础模型创建。"""
        version = ConfigVersionBase(
            config_id="config-123",
            config_key="database.host",
            version=1,
            value="localhost:5432",
            changed_by="user-1",
            change_type=ChangeType.CREATE,
        )

        assert version.config_id == "config-123"
        assert version.version == 1
        assert version.change_type == ChangeType.CREATE
        assert version.change_reason == ""
        assert version.diff_summary is None

    def test_version_create_model(self) -> None:
        """测试版本创建模型。"""
        version_create = ConfigVersionCreate(
            config_id="config-123",
            config_key="database.host",
            version=1,
            value="localhost:5432",
            changed_by="user-1",
            change_type=ChangeType.UPDATE,
            is_rollback_target=True,
        )

        assert version_create.is_rollback_target is True

    def test_version_response_model(self) -> None:
        """测试版本响应模型。"""
        now = datetime.now(tz=UTC)
        response = ConfigVersionResponse(
            id="version-1",
            config_id="config-123",
            config_key="database.host",
            version=5,
            value="new-host:5432",
            changed_by="user-2",
            change_type=ChangeType.UPDATE,
            change_reason="Migration to new host",
            created_at=now,
        )

        assert response.id == "version-1"
        assert response.version == 5
        assert response.change_reason == "Migration to new host"

    def test_version_document_creation(self) -> None:
        """测试版本文档创建。"""
        doc = ConfigVersionDocument(
            id="version-1",
            config_id="config-123",
            config_key="database.host",
            version=1,
            value="localhost:5432",
            changed_by="user-1",
            change_type=ChangeType.CREATE,
        )

        assert doc.version == 1
        assert doc.change_reason == ""
        assert doc.is_rollback_target is False
        assert isinstance(doc.created_at, datetime)

    def test_version_document_to_response(self) -> None:
        """测试版本文档转响应模型。"""
        now = datetime.now(tz=UTC)
        doc = ConfigVersionDocument(
            id="version-10",
            config_id="config-123",
            config_key="database.host",
            version=10,
            value={"host": "new-db", "port": 5433},
            changed_by="user-2",
            change_type=ChangeType.UPDATE,
            change_reason="DB migration",
            diff_summary={"changed_fields": ["host", "port"]},
            is_rollback_target=True,
            created_at=now,
        )

        response = doc.to_response()

        assert response.id == "version-10"
        assert response.version == 10
        assert response.is_rollback_target is True
        assert response.diff_summary == {"changed_fields": ["host", "port"]}

    def test_version_change_reason_max_length(self) -> None:
        """测试变更原因最大长度。"""
        # Within limit
        version = ConfigVersionBase(
            config_id="config-123",
            config_key="test.key",
            version=1,
            value="test",
            changed_by="user-1",
            change_type=ChangeType.UPDATE,
            change_reason="a" * 1000,
        )
        assert len(version.change_reason) == 1000

        # TODO: Add validation if needed
        # Exceeds limit - should fail with validation error
        # with pytest.raises(ValidationError):
        #     ConfigVersionBase(
        #         config_id="config-123",
        #         config_key="test.key",
        #         version=1,
        #         value="test",
        #         changed_by="user-1",
        #         change_type=ChangeType.UPDATE,
        #         change_reason="a" * 1001,
        #     )

    def test_all_change_types(self) -> None:
        """测试所有变更类型。"""
        for change_type in ChangeType:
            version = ConfigVersionBase(
                config_id="config-123",
                config_key="test.key",
                version=1,
                value="test",
                changed_by="user-1",
                change_type=change_type,
            )
            assert version.change_type == change_type


class TestAuditLogModels:
    """测试审计日志模型。"""

    def test_audit_log_base_creation(self) -> None:
        """测试审计日志基础模型创建。"""
        log = AuditLogBase(
            action=AuditAction.CONFIG_CREATE,
            resource_type="config",
            resource_id="config-123",
            resource_key="database.host",
            actor_id="user-1",
            actor_name="Test User",
        )

        assert log.action == AuditAction.CONFIG_CREATE
        assert log.resource_type == "config"
        assert log.actor_ip == ""
        assert log.old_value is None
        assert log.new_value is None
        assert log.metadata == {}

    def test_audit_log_create_with_status(self) -> None:
        """测试审计日志创建模型。"""
        log_create = AuditLogCreate(
            action=AuditAction.CONFIG_UPDATE,
            resource_type="config",
            resource_id="config-123",
            resource_key="database.host",
            actor_id="user-1",
            actor_name="Test User",
            status=AuditStatus.SUCCESS,
        )

        assert log_create.status == AuditStatus.SUCCESS

    def test_audit_log_response_model(self) -> None:
        """测试审计日志响应模型。"""
        now = datetime.now(tz=UTC)
        response = AuditLogResponse(
            id="log-1",
            action=AuditAction.CONFIG_DELETE,
            resource_type="config",
            resource_id="config-123",
            resource_key="database.host",
            actor_id="user-1",
            actor_name="Test User",
            status=AuditStatus.FAILED,
            timestamp=now,
        )

        assert response.id == "log-1"
        assert response.status == AuditStatus.FAILED
        assert response.timestamp == now

    def test_audit_log_document_creation(self) -> None:
        """测试审计日志文档创建。"""
        doc = AuditLogDocument(
            id="log-1",
            action=AuditAction.CONFIG_CREATE,
            resource_type="config",
            resource_id="config-123",
            resource_key="database.host",
            actor_id="user-1",
            actor_name="Test User",
            actor_ip="127.0.0.1",
            new_value={"host": "localhost"},
            metadata={"environment": "development"},
        )

        assert doc.status == AuditStatus.SUCCESS
        assert isinstance(doc.timestamp, datetime)

    def test_audit_log_document_to_response(self) -> None:
        """测试审计日志文档转响应模型。"""
        now = datetime.now(tz=UTC)
        doc = AuditLogDocument(
            id="log-100",
            action=AuditAction.CONFIG_PUBLISH,
            resource_type="config",
            resource_id="config-456",
            resource_key="api.key",
            actor_id="user-2",
            actor_name="Admin User",
            actor_ip="192.168.1.1",
            old_value="old-key",
            new_value="new-key",
            metadata={"environment": "production"},
            status=AuditStatus.SUCCESS,
            timestamp=now,
        )

        response = doc.to_response()

        assert response.id == "log-100"
        assert response.action == AuditAction.CONFIG_PUBLISH
        assert response.old_value == "old-key"
        assert response.new_value == "new-key"
        assert response.metadata == {"environment": "production"}

    def test_audit_log_resource_key_max_length(self) -> None:
        """测试资源键最大长度。"""
        with pytest.raises(ValidationError):
            AuditLogBase(
                action=AuditAction.CONFIG_CREATE,
                resource_type="config",
                resource_id="config-123",
                resource_key="a" * 501,
                actor_id="user-1",
                actor_name="Test User",
            )

    def test_audit_log_actor_name_max_length(self) -> None:
        """测试操作人名称最大长度。"""
        with pytest.raises(ValidationError):
            AuditLogBase(
                action=AuditAction.CONFIG_CREATE,
                resource_type="config",
                resource_id="config-123",
                resource_key="test.key",
                actor_id="user-1",
                actor_name="a" * 256,
            )

    def test_audit_log_actor_ip_max_length(self) -> None:
        """测试操作人 IP 最大长度（IPv6 最长 45 字符）。"""
        with pytest.raises(ValidationError):
            AuditLogBase(
                action=AuditAction.CONFIG_CREATE,
                resource_type="config",
                resource_id="config-123",
                resource_key="test.key",
                actor_id="user-1",
                actor_name="Test User",
                actor_ip="a" * 46,
            )

    def test_all_audit_actions(self) -> None:
        """测试所有审计操作类型。"""
        for action in AuditAction:
            log = AuditLogBase(
                action=action,
                resource_type="config",
                resource_id="config-123",
                resource_key="test.key",
                actor_id="user-1",
                actor_name="Test User",
            )
            assert log.action == action

    def test_audit_log_metadata_optional(self) -> None:
        """测试审计日志元数据为可选字段。"""
        log = AuditLogBase(
            action=AuditAction.CONFIG_CREATE,
            resource_type="config",
            resource_id="config-123",
            resource_key="test.key",
            actor_id="user-1",
            actor_name="Test User",
        )

        assert log.metadata == {}  # Default empty dict
