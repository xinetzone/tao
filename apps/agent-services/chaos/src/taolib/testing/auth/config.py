"""认证配置模块。

提供不可变的认证配置容器，通过构造函数注入所有参数。
"""

import os
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Self


@dataclass(frozen=True, slots=True)
class AuthConfig:
    """认证配置。

    所有认证参数通过构造函数注入，不依赖全局 settings 单例。

    Args:
        jwt_secret: JWT 签名密钥（必填）
        jwt_algorithm: JWT 签名算法
        access_token_ttl: Access Token 有效期
        refresh_token_ttl: Refresh Token 有效期
        token_issuer: 可选的 JWT ``iss`` 声明
        blacklist_key_prefix: Redis 黑名单键前缀
    """

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_ttl: timedelta = field(default_factory=lambda: timedelta(hours=1))
    refresh_token_ttl: timedelta = field(default_factory=lambda: timedelta(days=30))
    token_issuer: str | None = None
    blacklist_key_prefix: str = "taolib:auth:blacklist:"

    @classmethod
    def from_env(cls, prefix: str = "TAOLIB_AUTH_") -> Self:
        """从环境变量创建配置。

        Args:
            prefix: 环境变量前缀

        Returns:
            AuthConfig 实例

        Raises:
            ValueError: 如果必填的 JWT_SECRET 未设置
        """
        secret = os.environ.get(f"{prefix}JWT_SECRET", "")
        if not secret:
            msg = f"环境变量 {prefix}JWT_SECRET 未设置"
            raise ValueError(msg)
        if len(secret) < 32:
            msg = (
                f"环境变量 {prefix}JWT_SECRET 长度不足"
                f"（当前 {len(secret)}，HS256 要求至少 32 字符）"
            )
            raise ValueError(msg)

        algorithm = os.environ.get(f"{prefix}JWT_ALGORITHM", "HS256")
        issuer = os.environ.get(f"{prefix}TOKEN_ISSUER")

        access_minutes = int(
            os.environ.get(f"{prefix}ACCESS_TOKEN_MINUTES", "60"),
        )
        refresh_days = int(
            os.environ.get(f"{prefix}REFRESH_TOKEN_DAYS", "30"),
        )
        blacklist_prefix = os.environ.get(
            f"{prefix}BLACKLIST_KEY_PREFIX",
            "taolib:auth:blacklist:",
        )

        return cls(
            jwt_secret=secret,
            jwt_algorithm=algorithm,
            access_token_ttl=timedelta(minutes=access_minutes),
            refresh_token_ttl=timedelta(days=refresh_days),
            token_issuer=issuer,
            blacklist_key_prefix=blacklist_prefix,
        )
