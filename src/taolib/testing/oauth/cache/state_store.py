"""OAuth CSRF State 存储模块。

使用 Redis 存储和验证 OAuth 流程中的 CSRF state 参数。
"""

import json
import secrets
from typing import Any

from .keys import oauth_state_key


class OAuthStateStore:
    """OAuth CSRF State 存储。

    基于 Redis 的 state 参数管理，支持一次性消费和自动过期。

    Args:
        redis_client: Redis 异步客户端
        ttl_seconds: state 有效期（秒），默认 600（10 分钟）
    """

    def __init__(self, redis_client, ttl_seconds: int = 600) -> None:
        """初始化 State 存储。

        Args:
            redis_client: Redis 异步客户端
            ttl_seconds: state 有效期（秒）
        """
        self._redis = redis_client
        self._ttl = ttl_seconds

    async def create_state(self, extra_data: dict[str, Any] | None = None) -> str:
        """创建新的 CSRF state token。

        Args:
            extra_data: 附加数据（如 return_url, link_to_user_id）

        Returns:
            state token 字符串
        """
        state = secrets.token_urlsafe(32)
        key = oauth_state_key(state)
        value = json.dumps(extra_data) if extra_data else "{}"
        await self._redis.set(key, value, ex=self._ttl)
        return state

    async def validate_and_consume(self, state: str) -> dict[str, Any] | None:
        """验证并消费 state token（一次性使用）。

        原子性地读取并删除 state，防止重放攻击。

        Args:
            state: 待验证的 state token

        Returns:
            附加数据字典，如果 state 无效/已过期/已消费则返回 None
        """
        key = oauth_state_key(state)
        value = await self._redis.get(key)
        if value is None:
            return None
        await self._redis.delete(key)
        if isinstance(value, bytes):
            value = value.decode()
        return json.loads(value)


