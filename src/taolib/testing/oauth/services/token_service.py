"""OAuth Token 服务模块。

管理 OAuth Token 的加密存储和自动刷新。
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from ..crypto.token_encryption import TokenEncryptor
from ..errors import OAuthRefreshNotSupported, OAuthTokenRefreshError
from ..models.connection import OAuthConnectionDocument
from ..models.enums import (
    OAuthActivityAction,
    OAuthActivityStatus,
    OAuthConnectionStatus,
)
from ..providers import ProviderRegistry
from ..repository.activity_repo import OAuthActivityLogRepository
from ..repository.connection_repo import OAuthConnectionRepository
from ..repository.credential_repo import OAuthAppCredentialRepository

REFRESH_BUFFER_MINUTES = 5


class OAuthTokenService:
    """OAuth Token 服务。

    处理 OAuth Token 的加密、解密和自动刷新。

    Args:
        token_encryptor: Token 加密器
        connection_repo: 连接仓储
        credential_repo: 凭证仓储
        activity_repo: 活动日志仓储
        provider_registry: 提供商注册表
    """

    def __init__(
        self,
        token_encryptor: TokenEncryptor,
        connection_repo: OAuthConnectionRepository,
        credential_repo: OAuthAppCredentialRepository,
        activity_repo: OAuthActivityLogRepository,
        provider_registry: ProviderRegistry,
    ) -> None:
        self._encryptor = token_encryptor
        self._connection_repo = connection_repo
        self._credential_repo = credential_repo
        self._activity_repo = activity_repo
        self._provider_registry = provider_registry

    def decrypt_access_token(self, connection: OAuthConnectionDocument) -> str:
        """解密连接的 Access Token。

        Args:
            connection: 连接文档

        Returns:
            明文 Access Token
        """
        return self._encryptor.decrypt(connection.access_token_encrypted)

    async def refresh_if_expired(
        self, connection: OAuthConnectionDocument
    ) -> OAuthConnectionDocument:
        """如果 Token 即将过期则刷新。

        在 Token 过期前 5 分钟主动刷新。

        Args:
            connection: 连接文档

        Returns:
            更新后的连接文档（如果刷新了）或原始文档
        """
        if not connection.token_expires_at:
            return connection

        buffer = datetime.now(UTC) + timedelta(minutes=REFRESH_BUFFER_MINUTES)
        if connection.token_expires_at > buffer:
            return connection

        if not connection.refresh_token_encrypted:
            await self._connection_repo.update(
                connection.id,
                {"status": str(OAuthConnectionStatus.EXPIRED)},
            )
            raise OAuthTokenRefreshError("无 Refresh Token 且 Access Token 已过期")

        try:
            refresh_token = self._encryptor.decrypt(connection.refresh_token_encrypted)

            credential = await self._credential_repo.find_by_provider(
                connection.provider
            )
            if not credential:
                raise OAuthTokenRefreshError(f"未找到 {connection.provider} 的凭证")

            client_secret = self._encryptor.decrypt(credential.client_secret_encrypted)

            provider = self._provider_registry.get(connection.provider)
            token_data = await provider.refresh_access_token(
                refresh_token=refresh_token,
                client_id=credential.client_id,
                client_secret=client_secret,
            )

            new_access = token_data.get("access_token", "")
            new_refresh = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in")

            updates: dict[str, Any] = {
                "access_token_encrypted": self._encryptor.encrypt(new_access),
                "updated_at": datetime.now(UTC),
            }
            if new_refresh:
                updates["refresh_token_encrypted"] = self._encryptor.encrypt(
                    new_refresh
                )
            if expires_in:
                updates["token_expires_at"] = datetime.now(UTC) + timedelta(
                    seconds=int(expires_in)
                )

            updated = await self._connection_repo.update(connection.id, updates)

            await self._activity_repo.log_activity(
                action=OAuthActivityAction.TOKEN_REFRESH,
                status=OAuthActivityStatus.SUCCESS,
                provider=connection.provider,
                user_id=connection.user_id,
                connection_id=connection.id,
            )

            return updated or connection

        except OAuthRefreshNotSupported:
            await self._connection_repo.update(
                connection.id,
                {"status": str(OAuthConnectionStatus.EXPIRED)},
            )
            raise OAuthTokenRefreshError(f"{connection.provider} 不支持 Token 刷新")
        except OAuthTokenRefreshError:
            raise
        except Exception as e:
            await self._activity_repo.log_activity(
                action=OAuthActivityAction.TOKEN_REFRESH,
                status=OAuthActivityStatus.FAILED,
                provider=connection.provider,
                user_id=connection.user_id,
                connection_id=connection.id,
                metadata={"error": str(e)},
            )
            raise OAuthTokenRefreshError(f"Token 刷新失败: {e}")


