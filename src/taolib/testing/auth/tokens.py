"""JWT 令牌服务。

提供 JWT 令牌的创建、解码和验证功能。
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from .config import AuthConfig
from .errors import TokenExpiredError, TokenInvalidError
from .models import TokenPair, TokenPayload


class JWTService:
    """JWT 令牌服务。

    以 ``AuthConfig`` 注入初始化，提供令牌创建和验证的完整功能。

    Args:
        config: 认证配置实例
    """

    def __init__(self, config: AuthConfig) -> None:
        self._config = config

    @property
    def config(self) -> AuthConfig:
        """获取认证配置。"""
        return self._config

    def create_access_token(
        self,
        user_id: str,
        roles: list[str],
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """生成 Access Token。

        Args:
            user_id: 用户 ID
            roles: 用户角色列表
            extra_claims: 额外的 JWT 声明

        Returns:
            JWT Token 字符串
        """
        now = datetime.now(UTC)
        expire = now + self._config.access_token_ttl
        payload: dict[str, Any] = {
            "sub": user_id,
            "roles": roles,
            "exp": expire,
            "iat": now,
            "type": "access",
            "jti": str(uuid.uuid4()),
        }
        if self._config.token_issuer is not None:
            payload["iss"] = self._config.token_issuer
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(
            payload,
            self._config.jwt_secret,
            algorithm=self._config.jwt_algorithm,
        )

    def create_refresh_token(
        self,
        user_id: str,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """生成 Refresh Token。

        Refresh Token 不包含 roles，刷新时应重新从用户系统获取最新角色。

        Args:
            user_id: 用户 ID
            extra_claims: 额外的 JWT 声明

        Returns:
            JWT Token 字符串
        """
        now = datetime.now(UTC)
        expire = now + self._config.refresh_token_ttl
        payload: dict[str, Any] = {
            "sub": user_id,
            "roles": [],
            "exp": expire,
            "iat": now,
            "type": "refresh",
            "jti": str(uuid.uuid4()),
        }
        if self._config.token_issuer is not None:
            payload["iss"] = self._config.token_issuer
        if extra_claims:
            payload.update(extra_claims)
        return jwt.encode(
            payload,
            self._config.jwt_secret,
            algorithm=self._config.jwt_algorithm,
        )

    def create_token_pair(
        self,
        user_id: str,
        roles: list[str],
    ) -> TokenPair:
        """同时生成 Access Token 和 Refresh Token。

        Args:
            user_id: 用户 ID
            roles: 用户角色列表

        Returns:
            TokenPair 实例
        """
        access_token = self.create_access_token(user_id, roles)
        refresh_token = self.create_refresh_token(user_id)
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(self._config.access_token_ttl.total_seconds()),
        )

    def decode_token(self, token: str) -> TokenPayload:
        """解码任意类型的 JWT 令牌。

        Args:
            token: JWT Token 字符串

        Returns:
            TokenPayload 实例

        Raises:
            TokenExpiredError: 如果令牌已过期
            TokenInvalidError: 如果令牌无效
        """
        try:
            payload = jwt.decode(
                token,
                self._config.jwt_secret,
                algorithms=[self._config.jwt_algorithm],
            )
        except ExpiredSignatureError:
            raise TokenExpiredError
        except JWTError as e:
            raise TokenInvalidError(detail=str(e))

        return self._payload_from_dict(payload)

    def verify_access_token(self, token: str) -> TokenPayload:
        """验证 Access Token。

        解码令牌并确认类型为 ``"access"``。

        Args:
            token: JWT Token 字符串

        Returns:
            TokenPayload 实例

        Raises:
            TokenExpiredError: 如果令牌已过期
            TokenInvalidError: 如果令牌无效或类型不正确
        """
        payload = self.decode_token(token)
        if payload.type != "access":
            raise TokenInvalidError(
                message="令牌类型不正确",
                detail=f"期望 access，实际为 {payload.type}",
            )
        return payload

    def verify_refresh_token(self, token: str) -> TokenPayload:
        """验证 Refresh Token。

        解码令牌并确认类型为 ``"refresh"``。

        Args:
            token: JWT Token 字符串

        Returns:
            TokenPayload 实例

        Raises:
            TokenExpiredError: 如果令牌已过期
            TokenInvalidError: 如果令牌无效或类型不正确
        """
        payload = self.decode_token(token)
        if payload.type != "refresh":
            raise TokenInvalidError(
                message="令牌类型不正确",
                detail=f"期望 refresh，实际为 {payload.type}",
            )
        return payload

    @staticmethod
    def _payload_from_dict(data: dict[str, Any]) -> TokenPayload:
        """从字典构建 TokenPayload。

        兼容旧版令牌（可能缺少 jti/iat 字段）。

        Args:
            data: JWT payload 字典

        Returns:
            TokenPayload 实例
        """
        exp_value = data.get("exp")
        if isinstance(exp_value, int | float):
            exp_dt = datetime.fromtimestamp(exp_value, tz=UTC)
        else:
            exp_dt = exp_value

        iat_value = data.get("iat")
        if isinstance(iat_value, int | float):
            iat_dt = datetime.fromtimestamp(iat_value, tz=UTC)
        elif iat_value is None:
            iat_dt = datetime.now(UTC)
        else:
            iat_dt = iat_value

        return TokenPayload(
            sub=data.get("sub", ""),
            roles=data.get("roles", []),
            exp=exp_dt,
            iat=iat_dt,
            type=data.get("type", "access"),
            jti=data.get("jti", ""),
        )


