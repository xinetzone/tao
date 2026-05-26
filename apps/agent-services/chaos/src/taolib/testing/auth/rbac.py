"""通用 RBAC 策略引擎。

提供与业务领域解耦的基于角色的访问控制。
"""

from dataclasses import dataclass, field
from typing import Any, Self


@dataclass(frozen=True, slots=True)
class Permission:
    """权限定义。

    Args:
        resource: 资源类型
        action: 操作类型
    """

    resource: str
    action: str


@dataclass(slots=True)
class RoleDefinition:
    """角色定义。

    Args:
        name: 角色名称
        description: 角色描述
        permissions: 权限列表
        scopes: 作用域映射，键为作用域类型，值为允许的范围列表。
            ``None`` 值表示该作用域无限制。
    """

    name: str
    description: str
    permissions: list[Permission] = field(default_factory=list)
    scopes: dict[str, list[str] | None] = field(default_factory=dict)


class RBACPolicy:
    """RBAC 策略引擎。

    提供基于角色的权限检查和作用域验证。

    Args:
        roles: 角色名称到 RoleDefinition 的映射
    """

    def __init__(self, roles: dict[str, RoleDefinition]) -> None:
        self._roles = dict(roles)

    def get_role(self, name: str) -> RoleDefinition | None:
        """获取角色定义。

        Args:
            name: 角色名称

        Returns:
            角色定义，如不存在返回 None
        """
        return self._roles.get(name)

    def has_permission(
        self,
        user_roles: list[str],
        resource: str,
        action: str,
    ) -> bool:
        """检查用户角色列表中是否有任何角色拥有指定权限。

        Args:
            user_roles: 用户拥有的角色名称列表
            resource: 资源类型
            action: 操作类型

        Returns:
            是否有权限
        """
        for role_name in user_roles:
            role_def = self._roles.get(role_name)
            if role_def is None:
                continue
            for perm in role_def.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        return False

    def has_scope(
        self,
        user_roles: list[str],
        scope_type: str,
        scope_value: str,
    ) -> bool:
        """检查用户角色列表中是否有任何角色在指定作用域内。

        Args:
            user_roles: 用户拥有的角色名称列表
            scope_type: 作用域类型（如 ``"environment"``, ``"service"``）
            scope_value: 作用域值（如 ``"production"``, ``"auth-service"``）

        Returns:
            是否在作用域内
        """
        for role_name in user_roles:
            role_def = self._roles.get(role_name)
            if role_def is None:
                continue
            scope_values = role_def.scopes.get(scope_type)
            if scope_values is None:
                # None 表示该作用域无限制
                return True
            if scope_value in scope_values:
                return True
        return False

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, Any]]) -> Self:
        """从字典构建 RBAC 策略。

        兼容现有 ``RBACService.SYSTEM_ROLES`` 的数据格式。

        Args:
            data: 角色名称到角色数据字典的映射。每个角色数据应包含：
                - ``description``: 角色描述
                - ``permissions``: 权限列表，每项含 ``resource`` 和 ``actions``
                - 其他以 ``_scope`` 结尾的键将被解析为作用域

        Returns:
            RBACPolicy 实例
        """
        roles: dict[str, RoleDefinition] = {}
        for role_name, role_data in data.items():
            permissions: list[Permission] = []
            for perm_data in role_data.get("permissions", []):
                resource = perm_data.get("resource", "")
                for action in perm_data.get("actions", []):
                    permissions.append(Permission(resource=resource, action=action))

            scopes: dict[str, list[str] | None] = {}
            for key, value in role_data.items():
                if key.endswith("_scope"):
                    scope_type = key.removesuffix("_scope")
                    if value is None:
                        scopes[scope_type] = None
                    else:
                        scopes[scope_type] = [
                            v.value if hasattr(v, "value") else str(v) for v in value
                        ]

            roles[role_name] = RoleDefinition(
                name=role_name,
                description=role_data.get("description", ""),
                permissions=permissions,
                scopes=scopes,
            )
        return cls(roles)


