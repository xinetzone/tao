"""通用 JWT 认证中间件。

提供无状态、可扩展的 JWT 认证，支持令牌黑名单、API 密钥备选认证和 RBAC。

基础用法::

    import os
    from taolib.testing.auth import AuthConfig, JWTService

    # 生产环境：从环境变量获取密钥（必须 >= 32 字符）
    jwt_secret = os.environ.get("JWT_SECRET", "")
    if not jwt_secret or len(jwt_secret) < 32:
        raise ValueError("JWT_SECRET must be set and >= 32 characters")

    config = AuthConfig(jwt_secret=jwt_secret)
    jwt_service = JWTService(config)
    token_pair = jwt_service.create_token_pair("user-123", ["admin"])

FastAPI 集成::

    import os
    from taolib.testing.auth import AuthConfig, JWTService, AuthenticatedUser
    from taolib.testing.auth.fastapi.dependencies import create_auth_dependency

    jwt_secret = os.environ.get("JWT_SECRET", "")
    config = AuthConfig(jwt_secret=jwt_secret)
    jwt_service = JWTService(config)
    auth = create_auth_dependency(jwt_service)

    @app.get("/protected")
    async def protected(user: AuthenticatedUser = Depends(auth)):
        return {"user_id": user.user_id}
"""

from .api_key import APIKeyLookupProtocol, StaticAPIKeyLookup
from .blacklist import (
    InMemoryTokenBlacklist,
    NullTokenBlacklist,
    RedisTokenBlacklist,
    TokenBlacklistProtocol,
)
from .config import AuthConfig
from .errors import (
    APIKeyInvalidError,
    AuthError,
    InsufficientPermissionError,
    TokenBlacklistedError,
    TokenExpiredError,
    TokenInvalidError,
)
from .models import AuthenticatedUser, TokenPair, TokenPayload
from .rbac import Permission, RBACPolicy, RoleDefinition
from .tokens import JWTService

__all__ = [
    # 配置
    "AuthConfig",
    # 核心服务
    "JWTService",
    # 模型
    "AuthenticatedUser",
    "TokenPair",
    "TokenPayload",
    # 异常
    "APIKeyInvalidError",
    "AuthError",
    "InsufficientPermissionError",
    "TokenBlacklistedError",
    "TokenExpiredError",
    "TokenInvalidError",
    # 黑名单
    "InMemoryTokenBlacklist",
    "NullTokenBlacklist",
    "RedisTokenBlacklist",
    "TokenBlacklistProtocol",
    # API Key
    "APIKeyLookupProtocol",
    "StaticAPIKeyLookup",
    # RBAC
    "Permission",
    "RBACPolicy",
    "RoleDefinition",
]


