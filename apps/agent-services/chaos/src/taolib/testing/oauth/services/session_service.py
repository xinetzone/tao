"""OAuth 会话服务模块。

管理跨服务的 OAuth 会话。
"""

import uuid
from datetime import UTC, datetime, timedelta

from ..cache.keys import oauth_session_key
from ..models.enums import OAuthProvider
from ..models.session import OAuthSessionDocument, OAuthSessionResponse
from ..repository.session_repo import OAuthSessionRepository


class OAuthSessionService:
    """OAuth 会话服务。

    创建和管理跨服务的 OAuth 会话，集成 JWT Token 生成。

    Args:
        session_repo: 会话仓储
        redis_client: Redis 异步客户端
        jwt_secret: JWT 密钥
        jwt_algorithm: JWT 算法
        access_token_expire_minutes: Access Token 过期时间（分钟）
        refresh_token_expire_days: Refresh Token 过期时间（天）
    """

    def __init__(
        self,
        session_repo: OAuthSessionRepository,
        redis_client,
        jwt_secret: str,
        jwt_algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._session_repo = session_repo
        self._redis = redis_client
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm
        self._access_expire_min = access_token_expire_minutes
        self._refresh_expire_days = refresh_token_expire_days

    def _create_jwt(
        self, user_id: str, roles: list[str], token_type: str, expires_delta: timedelta
    ) -> str:
        """创建 JWT Token。

        使用与 config_center 兼容的 Token 格式。

        Args:
            user_id: 用户 ID
            roles: 用户角色列表
            token_type: Token 类型 ("access" 或 "refresh")
            expires_delta: 过期时间增量

        Returns:
            JWT Token 字符串
        """
        from jose import jwt

        expire = datetime.now(UTC) + expires_delta
        payload = {
            "sub": user_id,
            "roles": roles,
            "exp": expire,
            "type": token_type,
        }
        return jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm)

    async def create_session(
        self,
        user_id: str,
        connection_id: str,
        provider: OAuthProvider | str,
        roles: list[str],
        ip_address: str = "",
        user_agent: str = "",
        session_ttl_hours: int = 24,
    ) -> dict:
        """创建新的 OAuth 会话。

        Args:
            user_id: 用户 ID
            connection_id: OAuth 连接 ID
            provider: OAuth 提供商
            roles: 用户角色列表
            ip_address: 客户端 IP
            user_agent: 客户端 User-Agent
            session_ttl_hours: 会话有效期（小时）

        Returns:
            包含 session_id、access_token、refresh_token 的字典
        """
        session_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        access_token = self._create_jwt(
            user_id,
            roles,
            "access",
            timedelta(minutes=self._access_expire_min),
        )
        refresh_token = self._create_jwt(
            user_id,
            roles,
            "refresh",
            timedelta(days=self._refresh_expire_days),
        )

        session_data = {
            "_id": session_id,
            "user_id": user_id,
            "provider": str(provider),
            "connection_id": connection_id,
            "jwt_access_token": access_token,
            "jwt_refresh_token": refresh_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "is_active": True,
            "created_at": now,
            "expires_at": now + timedelta(hours=session_ttl_hours),
            "last_activity_at": now,
        }

        await self._session_repo.create(session_data)

        cache_key = oauth_session_key(session_id)
        await self._redis.set(cache_key, user_id, ex=session_ttl_hours * 3600)

        return {
            "session_id": session_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self._access_expire_min * 60,
        }

    async def validate_session(self, session_id: str) -> OAuthSessionDocument | None:
        """验证会话有效性。

        优先从 Redis 缓存检查，回退到 MongoDB。

        Args:
            session_id: 会话 ID

        Returns:
            会话文档，无效则返回 None
        """
        cache_key = oauth_session_key(session_id)
        cached = await self._redis.get(cache_key)
        if cached:
            session = await self._session_repo.get_by_id(session_id)
            if session and session.is_active:
                return session

        session = await self._session_repo.get_by_id(session_id)
        if session is None or not session.is_active:
            return None
        if session.expires_at < datetime.now(UTC):
            return None

        return session

    async def refresh_session(self, session_id: str, roles: list[str]) -> dict | None:
        """刷新会话的 JWT Token。

        Args:
            session_id: 会话 ID
            roles: 用户角色列表

        Returns:
            新的 Token 字典，会话无效则返回 None
        """
        session = await self.validate_session(session_id)
        if not session:
            return None

        new_access = self._create_jwt(
            session.user_id,
            roles,
            "access",
            timedelta(minutes=self._access_expire_min),
        )

        await self._session_repo.touch_session(session_id)

        return {
            "access_token": new_access,
            "refresh_token": session.jwt_refresh_token,
            "token_type": "bearer",
        }

    async def revoke_session(self, session_id: str) -> bool:
        """撤销指定会话。

        Args:
            session_id: 会话 ID

        Returns:
            是否成功撤销
        """
        result = await self._session_repo.deactivate_session(session_id)
        cache_key = oauth_session_key(session_id)
        await self._redis.delete(cache_key)
        return result

    async def revoke_all_sessions(self, user_id: str) -> int:
        """撤销用户的所有会话。

        Args:
            user_id: 用户 ID

        Returns:
            撤销的会话数量
        """
        sessions = await self._session_repo.find_active_sessions(user_id)
        for session in sessions:
            cache_key = oauth_session_key(session.id)
            await self._redis.delete(cache_key)

        return await self._session_repo.deactivate_all_for_user(user_id)

    async def list_active_sessions(self, user_id: str) -> list[OAuthSessionResponse]:
        """列出用户的所有活跃会话。

        Args:
            user_id: 用户 ID

        Returns:
            会话响应列表
        """
        sessions = await self._session_repo.find_active_sessions(user_id)
        return [s.to_response() for s in sessions]


