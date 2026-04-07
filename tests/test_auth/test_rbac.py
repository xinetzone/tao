"""RBAC 策略引擎测试。"""

import pytest

from taolib.auth.rbac import Permission, RBACPolicy, RoleDefinition


class TestRBACPolicy:
    """测试 RBAC 策略。"""

    @pytest.fixture
    def policy(self) -> RBACPolicy:
        """创建测试用 RBAC 策略。"""
        return RBACPolicy(
            roles={
                "admin": RoleDefinition(
                    name="admin",
                    description="管理员",
                    permissions=[
                        Permission(resource="config", action="read"),
                        Permission(resource="config", action="create"),
                        Permission(resource="config", action="update"),
                        Permission(resource="config", action="delete"),
                        Permission(resource="user", action="read"),
                        Permission(resource="user", action="create"),
                    ],
                    scopes={"environment": None, "service": None},
                ),
                "editor": RoleDefinition(
                    name="editor",
                    description="编辑者",
                    permissions=[
                        Permission(resource="config", action="read"),
                        Permission(resource="config", action="create"),
                        Permission(resource="config", action="update"),
                    ],
                    scopes={
                        "environment": ["development", "staging"],
                        "service": None,
                    },
                ),
                "viewer": RoleDefinition(
                    name="viewer",
                    description="查看者",
                    permissions=[
                        Permission(resource="config", action="read"),
                    ],
                    scopes={
                        "environment": ["development"],
                        "service": ["web-app"],
                    },
                ),
            },
        )

    def test_admin_has_all_permissions(self, policy: RBACPolicy):
        """测试管理员拥有所有权限。"""
        assert policy.has_permission(["admin"], "config", "read")
        assert policy.has_permission(["admin"], "config", "create")
        assert policy.has_permission(["admin"], "config", "delete")
        assert policy.has_permission(["admin"], "user", "create")

    def test_editor_limited_permissions(self, policy: RBACPolicy):
        """测试编辑者有限权限。"""
        assert policy.has_permission(["editor"], "config", "read")
        assert policy.has_permission(["editor"], "config", "update")
        assert not policy.has_permission(["editor"], "config", "delete")
        assert not policy.has_permission(["editor"], "user", "create")

    def test_viewer_read_only(self, policy: RBACPolicy):
        """测试查看者只读。"""
        assert policy.has_permission(["viewer"], "config", "read")
        assert not policy.has_permission(["viewer"], "config", "create")
        assert not policy.has_permission(["viewer"], "config", "delete")

    def test_unknown_role_denied(self, policy: RBACPolicy):
        """测试未知角色拒绝。"""
        assert not policy.has_permission(["unknown"], "config", "read")

    def test_empty_roles_denied(self, policy: RBACPolicy):
        """测试空角色列表拒绝。"""
        assert not policy.has_permission([], "config", "read")

    def test_multiple_roles_combined(self, policy: RBACPolicy):
        """测试多角色权限合并。"""
        assert policy.has_permission(["viewer", "editor"], "config", "update")
        assert policy.has_permission(["viewer", "editor"], "config", "read")
        assert not policy.has_permission(["viewer", "editor"], "config", "delete")

    def test_scope_unrestricted(self, policy: RBACPolicy):
        """测试无限制作用域。"""
        assert policy.has_scope(["admin"], "environment", "production")
        assert policy.has_scope(["admin"], "environment", "development")
        assert policy.has_scope(["admin"], "service", "any-service")

    def test_scope_restricted(self, policy: RBACPolicy):
        """测试受限作用域。"""
        assert policy.has_scope(["editor"], "environment", "development")
        assert policy.has_scope(["editor"], "environment", "staging")
        assert not policy.has_scope(["editor"], "environment", "production")

    def test_scope_narrow(self, policy: RBACPolicy):
        """测试窄作用域。"""
        assert policy.has_scope(["viewer"], "environment", "development")
        assert not policy.has_scope(["viewer"], "environment", "production")
        assert policy.has_scope(["viewer"], "service", "web-app")
        assert not policy.has_scope(["viewer"], "service", "api-gateway")

    def test_scope_combined_roles(self, policy: RBACPolicy):
        """测试多角色作用域合并。"""
        # viewer 只有 development，editor 有 development + staging
        assert policy.has_scope(["viewer", "editor"], "environment", "staging")

    def test_scope_unknown_role(self, policy: RBACPolicy):
        """测试未知角色作用域拒绝。"""
        assert not policy.has_scope(["unknown"], "environment", "development")

    def test_get_role(self, policy: RBACPolicy):
        """测试获取角色定义。"""
        admin = policy.get_role("admin")
        assert admin is not None
        assert admin.name == "admin"
        assert admin.description == "管理员"

    def test_get_role_not_found(self, policy: RBACPolicy):
        """测试获取不存在的角色。"""
        assert policy.get_role("nonexistent") is None


class TestRBACPolicyFromDict:
    """测试从字典构建 RBAC 策略。"""

    def test_from_dict_basic(self):
        """测试基本的字典构建。"""
        data = {
            "admin": {
                "description": "管理员",
                "permissions": [
                    {"resource": "config", "actions": ["read", "create", "update"]},
                ],
                "environment_scope": None,
                "service_scope": None,
            },
            "viewer": {
                "description": "查看者",
                "permissions": [
                    {"resource": "config", "actions": ["read"]},
                ],
                "environment_scope": ["dev", "staging"],
                "service_scope": ["web"],
            },
        }

        policy = RBACPolicy.from_dict(data)
        assert policy.has_permission(["admin"], "config", "read")
        assert policy.has_permission(["admin"], "config", "create")
        assert not policy.has_permission(["viewer"], "config", "create")

        assert policy.has_scope(["admin"], "environment", "production")
        assert not policy.has_scope(["viewer"], "environment", "production")
        assert policy.has_scope(["viewer"], "environment", "dev")
        assert policy.has_scope(["viewer"], "service", "web")

    def test_from_dict_with_enum_values(self):
        """测试带枚举值的字典构建（兼容 config_center SYSTEM_ROLES）。"""
        from enum import Enum

        class Env(Enum):
            DEV = "development"
            PROD = "production"

        data = {
            "editor": {
                "description": "编辑者",
                "permissions": [
                    {"resource": "config", "actions": ["read", "update"]},
                ],
                "environment_scope": [Env.DEV],
                "service_scope": None,
            },
        }

        policy = RBACPolicy.from_dict(data)
        assert policy.has_scope(["editor"], "environment", "development")
        assert not policy.has_scope(["editor"], "environment", "production")
        assert policy.has_scope(["editor"], "service", "any-service")

    def test_from_dict_empty(self):
        """测试空字典构建。"""
        policy = RBACPolicy.from_dict({})
        assert not policy.has_permission(["admin"], "config", "read")
