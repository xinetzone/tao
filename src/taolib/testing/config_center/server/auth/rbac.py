"""RBAC 权限控制模块。

实现基于角色的访问控制（RBAC）逻辑。
"""

from typing import Any, ClassVar

from ...models.enums import Environment


class RBACService:
    """RBAC 权限服务。"""

    SYSTEM_ROLES: ClassVar[dict[str, dict[str, Any]]] = {
        "super_admin": {
            "description": "超级管理员",
            "permissions": [
                {
                    "resource": "config",
                    "actions": [
                        "read",
                        "create",
                        "update",
                        "delete",
                        "publish",
                        "rollback",
                    ],
                },
                {"resource": "version", "actions": ["read", "rollback"]},
                {"resource": "audit", "actions": ["read"]},
                {"resource": "user", "actions": ["read", "create", "update", "delete"]},
                {"resource": "role", "actions": ["read", "create", "update", "delete"]},
            ],
            "environment_scope": None,  # 所有环境
            "service_scope": None,
        },
        "config_admin": {
            "description": "配置管理员",
            "permissions": [
                {
                    "resource": "config",
                    "actions": [
                        "read",
                        "create",
                        "update",
                        "delete",
                        "publish",
                        "rollback",
                    ],
                },
                {"resource": "version", "actions": ["read", "rollback"]},
                {"resource": "audit", "actions": ["read"]},
            ],
            "environment_scope": None,
            "service_scope": None,
        },
        "config_editor": {
            "description": "配置编辑",
            "permissions": [
                {"resource": "config", "actions": ["read", "create", "update"]},
                {"resource": "version", "actions": ["read"]},
            ],
            "environment_scope": [Environment.DEVELOPMENT, Environment.STAGING],
            "service_scope": None,
        },
        "config_viewer": {
            "description": "配置查看者",
            "permissions": [
                {"resource": "config", "actions": ["read"]},
                {"resource": "version", "actions": ["read"]},
            ],
            "environment_scope": [Environment.DEVELOPMENT, Environment.STAGING],
            "service_scope": None,
        },
        "auditor": {
            "description": "审计员",
            "permissions": [
                {"resource": "audit", "actions": ["read"]},
                {"resource": "config", "actions": ["read"]},
                {"resource": "version", "actions": ["read"]},
            ],
            "environment_scope": None,
            "service_scope": None,
        },
    }

    def __init__(self) -> None:
        """初始化 RBAC 服务。"""
        self._role_cache: dict[str, dict[str, Any]] = {}

    def has_permission(
        self,
        user_roles: list[dict[str, Any]],
        resource: str,
        action: str,
    ) -> bool:
        """检查用户是否有指定权限。

        Args:
            user_roles: 用户角色列表
            resource: 资源类型
            action: 操作类型

        Returns:
            是否有权限
        """
        for role in user_roles:
            _ = role.get("name", "")
            permissions = role.get("permissions", [])
            for perm in permissions:
                if perm.get("resource") == resource and action in perm.get(
                    "actions", []
                ):
                    return True
        return False

    def can_access_environment(
        self,
        user_roles: list[dict[str, Any]],
        environment: Environment,
    ) -> bool:
        """检查用户是否有该环境的访问权限。

        Args:
            user_roles: 用户角色列表
            environment: 环境类型

        Returns:
            是否有权限访问该环境
        """
        for role in user_roles:
            env_scope = role.get("environment_scope")
            if env_scope is None:  # None 表示所有环境
                return True
            if environment in env_scope:
                return True
        return False

    def can_access_service(
        self,
        user_roles: list[dict[str, Any]],
        service: str,
    ) -> bool:
        """检查用户是否有该服务的访问权限。

        Args:
            user_roles: 用户角色列表
            service: 服务名称

        Returns:
            是否有权限访问该服务
        """
        for role in user_roles:
            svc_scope = role.get("service_scope")
            if svc_scope is None:  # None 表示所有服务
                return True
            if service in svc_scope:
                return True
        return False


