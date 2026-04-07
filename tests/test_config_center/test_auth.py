"""认证授权测试 - JWT 和 RBAC。"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from jose import JWTError, jwt

from taolib.config_center.models.enums import Environment
from taolib.config_center.server.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
)
from taolib.config_center.server.auth.rbac import RBACService


class TestJWTHandler:
    """测试 JWT 处理。"""

    @pytest.fixture
    def jwt_secret(self) -> str:
        """测试用 JWT 密钥。"""
        return "test-secret-key"

    @pytest.fixture
    def jwt_algorithm(self) -> str:
        """测试用 JWT 算法。"""
        return "HS256"

    def test_create_access_token(self, jwt_secret: str, jwt_algorithm: str) -> None:
        """测试创建 access token。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = jwt_algorithm
            mock_settings.access_token_expire_minutes = 15

            token = create_access_token("user-123", ["config_admin"])

            assert token is not None
            assert isinstance(token, str)

            # Decode and verify
            payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
            assert payload["sub"] == "user-123"
            assert payload["roles"] == ["config_admin"]
            assert payload["type"] == "access"
            assert "exp" in payload

    def test_create_access_token_custom_expiry(self, jwt_secret: str, jwt_algorithm: str) -> None:
        """测试创建带自定义过期时间的 access token。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = jwt_algorithm

            token = create_access_token(
                "user-123",
                ["config_viewer"],
                expires_delta=timedelta(hours=1),
            )

            payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
            assert payload["type"] == "access"

    def test_create_refresh_token(self, jwt_secret: str, jwt_algorithm: str) -> None:
        """测试创建 refresh token。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = jwt_algorithm
            mock_settings.refresh_token_expire_days = 7

            token = create_refresh_token("user-123")

            assert token is not None

            # Decode and verify
            payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
            assert payload["sub"] == "user-123"
            assert payload["type"] == "refresh"
            assert "exp" in payload

    def test_decode_valid_token(self, jwt_secret: str, jwt_algorithm: str) -> None:
        """测试解码有效 token。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = jwt_algorithm
            mock_settings.access_token_expire_minutes = 15

            token = create_access_token("user-123", ["admin"])
            payload = decode_token(token)

            assert payload["sub"] == "user-123"
            assert payload["roles"] == ["admin"]

    def test_decode_invalid_token_raises_error(self, jwt_secret: str) -> None:
        """测试解码无效 token 抛出异常。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = "HS256"

            invalid_token = "invalid.token.here"

            with pytest.raises(JWTError):
                decode_token(invalid_token)

    def test_verify_access_token_valid_type(self, jwt_secret: str, jwt_algorithm: str) -> None:
        """测试验证有效的 access token。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = jwt_algorithm
            mock_settings.access_token_expire_minutes = 15

            token = create_access_token("user-123", ["config_admin"])
            payload = verify_access_token(token)

            assert payload["sub"] == "user-123"
            assert payload["type"] == "access"

    def test_verify_access_token_rejects_refresh_token(self, jwt_secret: str, jwt_algorithm: str) -> None:
        """测试 refresh token 被 access token 验证拒绝。"""
        with patch("taolib.config_center.server.auth.jwt_handler.settings") as mock_settings:
            mock_settings.jwt_secret = jwt_secret
            mock_settings.jwt_algorithm = jwt_algorithm
            mock_settings.refresh_token_expire_days = 7

            refresh_token = create_refresh_token("user-123")

            with pytest.raises(JWTError, match="Invalid token type"):
                verify_access_token(refresh_token)


class TestRBACService:
    """测试 RBAC 权限服务。"""

    @pytest.fixture
    def rbac_service(self) -> RBACService:
        """创建 RBAC 服务实例。"""
        return RBACService()

    def test_system_roles_defined(self) -> None:
        """测试系统角色已定义。"""
        assert "super_admin" in RBACService.SYSTEM_ROLES
        assert "config_admin" in RBACService.SYSTEM_ROLES
        assert "config_editor" in RBACService.SYSTEM_ROLES
        assert "config_viewer" in RBACService.SYSTEM_ROLES
        assert "auditor" in RBACService.SYSTEM_ROLES

    def test_super_admin_has_all_permissions(self, rbac_service: RBACService) -> None:
        """测试超级管理员拥有所有权限。"""
        super_admin_role = [RBACService.SYSTEM_ROLES["super_admin"]]

        assert rbac_service.has_permission(super_admin_role, "config", "create")
        assert rbac_service.has_permission(super_admin_role, "config", "update")
        assert rbac_service.has_permission(super_admin_role, "config", "delete")
        assert rbac_service.has_permission(super_admin_role, "config", "publish")
        assert rbac_service.has_permission(super_admin_role, "user", "create")
        assert rbac_service.has_permission(super_admin_role, "role", "delete")

    def test_config_viewer_read_only(self, rbac_service: RBACService) -> None:
        """测试配置查看者只有读权限。"""
        viewer_role = [RBACService.SYSTEM_ROLES["config_viewer"]]

        assert rbac_service.has_permission(viewer_role, "config", "read")
        assert rbac_service.has_permission(viewer_role, "version", "read")
        assert not rbac_service.has_permission(viewer_role, "config", "create")
        assert not rbac_service.has_permission(viewer_role, "config", "update")
        assert not rbac_service.has_permission(viewer_role, "config", "delete")

    def test_config_editor_can_update_dev_staging(self, rbac_service: RBACService) -> None:
        """测试配置编辑者可以更新开发/测试环境。"""
        editor_role = [RBACService.SYSTEM_ROLES["config_editor"]]

        # Can edit configs
        assert rbac_service.has_permission(editor_role, "config", "create")
        assert rbac_service.has_permission(editor_role, "config", "update")

        # But limited to dev/staging environments
        assert rbac_service.can_access_environment(editor_role, Environment.DEVELOPMENT)
        assert rbac_service.can_access_environment(editor_role, Environment.STAGING)
        assert not rbac_service.can_access_environment(editor_role, Environment.PRODUCTION)
        assert not rbac_service.can_access_environment(editor_role, Environment.PRE_PRODUCTION)

    def test_auditor_read_only_audit(self, rbac_service: RBACService) -> None:
        """测试审计员只有审计读权限。"""
        auditor_role = [RBACService.SYSTEM_ROLES["auditor"]]

        assert rbac_service.has_permission(auditor_role, "audit", "read")
        assert rbac_service.has_permission(auditor_role, "config", "read")
        assert not rbac_service.has_permission(auditor_role, "config", "create")
        assert not rbac_service.has_permission(auditor_role, "user", "create")

    def test_no_permission_denied(self, rbac_service: RBACService) -> None:
        """测试无权限时拒绝访问。"""
        empty_roles: list[dict] = []

        assert not rbac_service.has_permission(empty_roles, "config", "read")
        assert not rbac_service.has_permission(empty_roles, "user", "delete")

    def test_unknown_resource_denied(self, rbac_service: RBACService) -> None:
        """测试未知资源拒绝访问。"""
        viewer_role = [RBACService.SYSTEM_ROLES["config_viewer"]]

        assert not rbac_service.has_permission(viewer_role, "unknown", "read")

    def test_unknown_action_denied(self, rbac_service: RBACService) -> None:
        """测试未知操作拒绝访问。"""
        viewer_role = [RBACService.SYSTEM_ROLES["config_viewer"]]

        assert not rbac_service.has_permission(viewer_role, "config", "execute")

    def test_can_access_environment_with_no_scope(self, rbac_service: RBACService) -> None:
        """测试无环境 scope 限制时可访问所有环境。"""
        admin_role = [RBACService.SYSTEM_ROLES["config_admin"]]

        assert rbac_service.can_access_environment(admin_role, Environment.DEVELOPMENT)
        assert rbac_service.can_access_environment(admin_role, Environment.PRODUCTION)
        assert rbac_service.can_access_environment(admin_role, Environment.STAGING)

    def test_can_access_service_with_no_scope(self, rbac_service: RBACService) -> None:
        """测试无服务 scope 限制时可访问所有服务。"""
        admin_role = [RBACService.SYSTEM_ROLES["config_admin"]]

        assert rbac_service.can_access_service(admin_role, "auth-service")
        assert rbac_service.can_access_service(admin_role, "api-gateway")
        assert rbac_service.can_access_service(admin_role, "any-service")

    def test_custom_role_with_specific_permissions(self, rbac_service: RBACService) -> None:
        """测试自定义角色带特定权限。"""
        custom_role = [{
            "name": "database_admin",
            "permissions": [
                {"resource": "config", "actions": ["read", "update"]},
            ],
            "environment_scope": [Environment.PRODUCTION],
            "service_scope": ["database-service"],
        }]

        assert rbac_service.has_permission(custom_role, "config", "read")
        assert rbac_service.has_permission(custom_role, "config", "update")
        assert not rbac_service.has_permission(custom_role, "config", "delete")

        assert rbac_service.can_access_environment(custom_role, Environment.PRODUCTION)
        assert not rbac_service.can_access_environment(custom_role, Environment.DEVELOPMENT)

        assert rbac_service.can_access_service(custom_role, "database-service")
        assert not rbac_service.can_access_service(custom_role, "other-service")

    def test_multiple_roles_combined_permissions(self, rbac_service: RBACService) -> None:
        """测试多角色组合权限。"""
        roles = [
            RBACService.SYSTEM_ROLES["config_viewer"],
            RBACService.SYSTEM_ROLES["auditor"],
        ]

        # From config_viewer
        assert rbac_service.has_permission(roles, "config", "read")

        # From auditor
        assert rbac_service.has_permission(roles, "audit", "read")

        # Neither role has this
        assert not rbac_service.has_permission(roles, "config", "delete")

    def test_system_roles_structure(self) -> None:
        """测试系统角色结构完整性。"""
        for role_name, role_data in RBACService.SYSTEM_ROLES.items():
            assert "description" in role_data
            assert "permissions" in role_data
            assert "environment_scope" in role_data
            assert "service_scope" in role_data

            # Permissions should be a list
            assert isinstance(role_data["permissions"], list)

            # Each permission should have resource and actions
            for perm in role_data["permissions"]:
                assert "resource" in perm
                assert "actions" in perm
                assert isinstance(perm["actions"], list)
