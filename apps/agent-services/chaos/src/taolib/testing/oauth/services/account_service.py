"""OAuth 账户服务模块。

管理 OAuth 身份与本地用户账户的关联。
"""

from datetime import UTC, datetime
from typing import Any

from ..crypto.token_encryption import TokenEncryptor
from ..errors import OAuthAlreadyLinkedError, OAuthCannotUnlinkError
from ..models.connection import OAuthConnectionDocument, OAuthConnectionResponse
from ..models.enums import (
    OAuthActivityAction,
    OAuthActivityStatus,
    OAuthConnectionStatus,
)
from ..models.profile import OAuthUserInfo
from ..repository.activity_repo import OAuthActivityLogRepository
from ..repository.connection_repo import OAuthConnectionRepository


class OAuthAccountService:
    """OAuth 账户服务。

    管理用户与 OAuth 提供商之间的关联关系。

    Args:
        connection_repo: 连接仓储
        activity_repo: 活动日志仓储
        token_encryptor: Token 加密器
    """

    def __init__(
        self,
        connection_repo: OAuthConnectionRepository,
        activity_repo: OAuthActivityLogRepository,
        token_encryptor: TokenEncryptor,
    ) -> None:
        self._connection_repo = connection_repo
        self._activity_repo = activity_repo
        self._token_encryptor = token_encryptor

    async def find_or_create_connection(
        self,
        user_info: OAuthUserInfo,
        token_data: dict[str, Any],
        ip_address: str = "",
        user_agent: str = "",
    ) -> tuple[OAuthConnectionDocument, bool]:
        """查找或创建 OAuth 连接。

        流程：
        1. 按 (provider, provider_user_id) 查找已存在的连接
        2. 如果找到，更新 Token 并返回
        3. 如果未找到，创建新连接（状态为 PENDING_ONBOARDING）

        Args:
            user_info: 标准化的用户信息
            token_data: Token 数据（含 access_token, refresh_token 等）
            ip_address: 客户端 IP
            user_agent: 客户端 User-Agent

        Returns:
            (connection, is_new_user) 元组
        """
        existing = await self._connection_repo.find_by_provider_user_id(
            user_info.provider, user_info.provider_user_id
        )

        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        token_expires_at = None
        if expires_in:
            token_expires_at = datetime.now(UTC) + __import__("datetime").timedelta(
                seconds=int(expires_in)
            )

        encrypted_access = self._token_encryptor.encrypt(access_token)
        encrypted_refresh = (
            self._token_encryptor.encrypt(refresh_token) if refresh_token else None
        )

        if existing:
            updates: dict[str, Any] = {
                "access_token_encrypted": encrypted_access,
                "refresh_token_encrypted": encrypted_refresh,
                "token_expires_at": token_expires_at,
                "last_used_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "display_name": user_info.display_name,
                "avatar_url": user_info.avatar_url,
            }
            if user_info.email:
                updates["email"] = user_info.email
            if existing.status == OAuthConnectionStatus.EXPIRED:
                updates["status"] = OAuthConnectionStatus.ACTIVE

            updated = await self._connection_repo.update(existing.id, updates)

            await self._activity_repo.log_activity(
                action=OAuthActivityAction.LOGIN,
                status=OAuthActivityStatus.SUCCESS,
                provider=user_info.provider,
                user_id=existing.user_id,
                connection_id=existing.id,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            return updated or existing, False

        scopes = token_data.get("scope", "").split() if token_data.get("scope") else []

        doc_data: dict[str, Any] = {
            "provider": str(user_info.provider),
            "provider_user_id": user_info.provider_user_id,
            "email": user_info.email,
            "display_name": user_info.display_name,
            "avatar_url": user_info.avatar_url,
            "user_id": "",
            "access_token_encrypted": encrypted_access,
            "refresh_token_encrypted": encrypted_refresh,
            "token_expires_at": token_expires_at,
            "scopes": scopes,
            "status": str(OAuthConnectionStatus.PENDING_ONBOARDING),
        }

        connection = await self._connection_repo.create(doc_data)
        return connection, True

    async def link_provider(
        self,
        user_id: str,
        user_info: OAuthUserInfo,
        token_data: dict[str, Any],
        ip_address: str = "",
        user_agent: str = "",
    ) -> OAuthConnectionDocument:
        """将新的提供商关联到已有用户。

        Args:
            user_id: 本地用户 ID
            user_info: 标准化的用户信息
            token_data: Token 数据
            ip_address: 客户端 IP
            user_agent: 客户端 User-Agent

        Returns:
            新创建的连接文档

        Raises:
            OAuthAlreadyLinkedError: 该提供商已关联到此用户
        """
        existing = await self._connection_repo.find_by_user_and_provider(
            user_id, user_info.provider
        )
        if existing:
            raise OAuthAlreadyLinkedError()

        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        token_expires_at = None
        if expires_in:
            token_expires_at = datetime.now(UTC) + __import__("datetime").timedelta(
                seconds=int(expires_in)
            )

        scopes = token_data.get("scope", "").split() if token_data.get("scope") else []

        doc_data: dict[str, Any] = {
            "provider": str(user_info.provider),
            "provider_user_id": user_info.provider_user_id,
            "email": user_info.email,
            "display_name": user_info.display_name,
            "avatar_url": user_info.avatar_url,
            "user_id": user_id,
            "access_token_encrypted": self._token_encryptor.encrypt(access_token),
            "refresh_token_encrypted": (
                self._token_encryptor.encrypt(refresh_token) if refresh_token else None
            ),
            "token_expires_at": token_expires_at,
            "scopes": scopes,
            "status": str(OAuthConnectionStatus.ACTIVE),
        }

        connection = await self._connection_repo.create(doc_data)

        await self._activity_repo.log_activity(
            action=OAuthActivityAction.LINK,
            status=OAuthActivityStatus.SUCCESS,
            provider=user_info.provider,
            user_id=user_id,
            connection_id=connection.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return connection

    async def unlink_provider(
        self,
        user_id: str,
        provider: str,
        has_password: bool = False,
        ip_address: str = "",
        user_agent: str = "",
    ) -> bool:
        """解除用户与提供商的关联。

        确保至少保留一种认证方式。

        Args:
            user_id: 用户 ID
            provider: 提供商名称
            has_password: 用户是否设置了密码
            ip_address: 客户端 IP
            user_agent: 客户端 User-Agent

        Returns:
            是否成功解除关联

        Raises:
            OAuthCannotUnlinkError: 无法解除最后一种认证方式
        """
        active_count = await self._connection_repo.count_active_for_user(user_id)
        if active_count <= 1 and not has_password:
            raise OAuthCannotUnlinkError()

        connection = await self._connection_repo.find_by_user_and_provider(
            user_id, provider
        )
        if not connection:
            return False

        await self._connection_repo.update(
            connection.id,
            {
                "status": str(OAuthConnectionStatus.REVOKED),
                "updated_at": datetime.now(UTC),
            },
        )

        await self._activity_repo.log_activity(
            action=OAuthActivityAction.UNLINK,
            status=OAuthActivityStatus.SUCCESS,
            provider=connection.provider,
            user_id=user_id,
            connection_id=connection.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return True

    async def get_user_connections(self, user_id: str) -> list[OAuthConnectionResponse]:
        """获取用户的所有 OAuth 连接。

        Args:
            user_id: 用户 ID

        Returns:
            连接响应列表
        """
        connections = await self._connection_repo.find_all_for_user(user_id)
        return [conn.to_response() for conn in connections]


