"""OAuth 管理服务模块。

提供 OAuth 应用凭证管理和活动监控功能。
"""

from datetime import UTC, datetime
from typing import Any

from ..crypto.token_encryption import TokenEncryptor
from ..models.activity import OAuthActivityLogResponse
from ..models.credential import (
    OAuthAppCredentialCreate,
    OAuthAppCredentialResponse,
    OAuthAppCredentialUpdate,
)
from ..models.enums import OAuthActivityAction, OAuthActivityStatus
from ..repository.activity_repo import OAuthActivityLogRepository
from ..repository.connection_repo import OAuthConnectionRepository
from ..repository.credential_repo import OAuthAppCredentialRepository


class OAuthAdminService:
    """OAuth 管理服务。

    提供凭证 CRUD、活动日志查询和连接统计功能。

    Args:
        credential_repo: 凭证仓储
        activity_repo: 活动日志仓储
        connection_repo: 连接仓储
        token_encryptor: Token 加密器
    """

    def __init__(
        self,
        credential_repo: OAuthAppCredentialRepository,
        activity_repo: OAuthActivityLogRepository,
        connection_repo: OAuthConnectionRepository,
        token_encryptor: TokenEncryptor,
    ) -> None:
        self._credential_repo = credential_repo
        self._activity_repo = activity_repo
        self._connection_repo = connection_repo
        self._encryptor = token_encryptor

    async def create_credential(
        self,
        data: OAuthAppCredentialCreate,
        admin_user_id: str,
    ) -> OAuthAppCredentialResponse:
        """创建 OAuth 应用凭证。

        Args:
            data: 凭证创建数据
            admin_user_id: 管理员用户 ID

        Returns:
            凭证响应（不含 client_secret）
        """
        doc_data: dict[str, Any] = {
            "provider": str(data.provider),
            "client_id": data.client_id,
            "client_secret_encrypted": self._encryptor.encrypt(data.client_secret),
            "display_name": data.display_name,
            "enabled": data.enabled,
            "allowed_scopes": data.allowed_scopes,
            "redirect_uri": data.redirect_uri,
            "created_by": admin_user_id,
        }

        credential = await self._credential_repo.create(doc_data)

        await self._activity_repo.log_activity(
            action=OAuthActivityAction.CREDENTIAL_CREATE,
            status=OAuthActivityStatus.SUCCESS,
            provider=data.provider,
            user_id=admin_user_id,
            metadata={"provider": str(data.provider), "client_id": data.client_id},
        )

        return credential.to_response()

    async def update_credential(
        self,
        credential_id: str,
        data: OAuthAppCredentialUpdate,
        admin_user_id: str,
    ) -> OAuthAppCredentialResponse | None:
        """更新 OAuth 应用凭证。

        Args:
            credential_id: 凭证 ID
            data: 凭证更新数据
            admin_user_id: 管理员用户 ID

        Returns:
            更新后的凭证响应，不存在则返回 None
        """
        updates: dict[str, Any] = {"updated_at": datetime.now(UTC)}

        if data.client_id is not None:
            updates["client_id"] = data.client_id
        if data.client_secret is not None:
            updates["client_secret_encrypted"] = self._encryptor.encrypt(
                data.client_secret
            )
        if data.display_name is not None:
            updates["display_name"] = data.display_name
        if data.enabled is not None:
            updates["enabled"] = data.enabled
        if data.allowed_scopes is not None:
            updates["allowed_scopes"] = data.allowed_scopes
        if data.redirect_uri is not None:
            updates["redirect_uri"] = data.redirect_uri

        updated = await self._credential_repo.update(credential_id, updates)
        if not updated:
            return None

        await self._activity_repo.log_activity(
            action=OAuthActivityAction.CREDENTIAL_UPDATE,
            status=OAuthActivityStatus.SUCCESS,
            user_id=admin_user_id,
            metadata={"credential_id": credential_id},
        )

        return updated.to_response()

    async def delete_credential(
        self,
        credential_id: str,
        admin_user_id: str,
    ) -> bool:
        """删除 OAuth 应用凭证。

        Args:
            credential_id: 凭证 ID
            admin_user_id: 管理员用户 ID

        Returns:
            是否成功删除
        """
        result = await self._credential_repo.delete(credential_id)

        if result:
            await self._activity_repo.log_activity(
                action=OAuthActivityAction.CREDENTIAL_DELETE,
                status=OAuthActivityStatus.SUCCESS,
                user_id=admin_user_id,
                metadata={"credential_id": credential_id},
            )

        return result

    async def list_credentials(self) -> list[OAuthAppCredentialResponse]:
        """列出所有 OAuth 应用凭证。

        Returns:
            凭证响应列表（不含 client_secret）
        """
        credentials = await self._credential_repo.find_all()
        return [c.to_response() for c in credentials]

    async def get_activity_logs(
        self,
        *,
        user_id: str | None = None,
        provider: str | None = None,
        action: str | None = None,
        status: str | None = None,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[OAuthActivityLogResponse]:
        """查询活动日志。

        Args:
            user_id: 按用户 ID 过滤
            provider: 按提供商过滤
            action: 按操作类型过滤
            status: 按状态过滤
            time_from: 起始时间
            time_to: 结束时间
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            活动日志响应列表
        """
        logs = await self._activity_repo.query_logs(
            user_id=user_id,
            provider=provider,
            action=action,
            status=status,
            time_from=time_from,
            time_to=time_to,
            skip=skip,
            limit=limit,
        )
        return [log.to_response() for log in logs]

    async def get_stats(self) -> dict[str, Any]:
        """获取 OAuth 连接和活动统计。

        Returns:
            统计数据字典
        """
        activity_stats = await self._activity_repo.get_stats()
        total_connections = await self._connection_repo.count()
        active_connections = await self._connection_repo.count({"status": "active"})

        return {
            **activity_stats,
            "total_connections": total_connections,
            "active_connections": active_connections,
        }
