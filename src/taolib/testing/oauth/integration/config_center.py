"""Config Center 集成桥接模块。

提供 OAuth 模块与 config_center 用户系统和 JWT 体系的桥接。
"""

from datetime import UTC, datetime
from typing import Any

from ..models.enums import OAuthConnectionStatus
from ..models.profile import OAuthUserInfo, OnboardingData
from ..repository.connection_repo import OAuthConnectionRepository


class ConfigCenterIntegration:
    """Config Center 集成桥接。

    连接 OAuth 模块与 config_center 的用户管理和 JWT Token 系统。

    Args:
        user_repo: config_center 的 UserRepository
        role_collection: MongoDB 角色集合
        jwt_secret: JWT 密钥
        jwt_algorithm: JWT 算法
    """

    def __init__(
        self,
        user_repo,
        role_collection,
        jwt_secret: str,
        jwt_algorithm: str = "HS256",
    ) -> None:
        self._user_repo = user_repo
        self._role_collection = role_collection
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm

    async def find_user_by_email(self, email: str):
        """按邮箱查找 config_center 用户。

        Args:
            email: 邮箱地址

        Returns:
            UserDocument 或 None
        """
        return await self._user_repo.find_by_email(email)

    async def create_user_from_oauth(
        self,
        user_info: OAuthUserInfo,
        onboarding: OnboardingData,
    ):
        """通过 OAuth 信息创建 config_center 用户。

        创建一个无密码的用户（使用占位密码哈希），仅通过 OAuth 认证。

        Args:
            user_info: OAuth 提供商的用户信息
            onboarding: 用户引导数据

        Returns:
            新创建的 UserDocument
        """
        import secrets

        from passlib.hash import bcrypt

        placeholder_password = secrets.token_urlsafe(32)
        password_hash = bcrypt.hash(placeholder_password)

        display_name = onboarding.display_name or user_info.display_name

        user_data: dict[str, Any] = {
            "username": onboarding.username,
            "password_hash": password_hash,
            "email": user_info.email,
            "display_name": display_name,
            "is_active": True,
            "role_ids": [],
            "last_login": datetime.now(UTC),
        }

        return await self._user_repo.create(user_data)

    async def get_user_roles(self, user_id: str) -> list[str]:
        """获取用户的角色名称列表。

        Args:
            user_id: 用户 ID

        Returns:
            角色名称列表
        """
        user_roles = await self._user_repo.get_user_roles(
            user_id, self._role_collection
        )
        return [role.get("name", "") for role in user_roles]

    async def complete_onboarding(
        self,
        connection_id: str,
        onboarding: OnboardingData,
        user_info: OAuthUserInfo,
        connection_repo: OAuthConnectionRepository,
    ) -> dict[str, Any]:
        """完成新用户引导流程。

        1. 按邮箱查找已有用户或创建新用户
        2. 更新 OAuth 连接，关联到用户
        3. 返回用户信息和角色

        Args:
            connection_id: OAuth 连接 ID
            onboarding: 引导数据
            user_info: OAuth 用户信息
            connection_repo: OAuth 连接仓储

        Returns:
            包含 user_id 和 roles 的字典
        """
        user = None
        if user_info.email:
            user = await self.find_user_by_email(user_info.email)

        if not user:
            user = await self.create_user_from_oauth(user_info, onboarding)

        roles = await self.get_user_roles(user.id)

        await connection_repo.update(
            connection_id,
            {
                "user_id": user.id,
                "status": str(OAuthConnectionStatus.ACTIVE),
                "updated_at": datetime.now(UTC),
            },
        )

        return {
            "user_id": user.id,
            "roles": roles,
            "user": user,
        }


