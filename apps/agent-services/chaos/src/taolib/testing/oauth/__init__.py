"""taolib.oauth — OAuth2 第三方登录模块。

支持 Google、GitHub 等多种 OAuth2 提供商的第三方登录，
提供完整的授权码流程、账户关联、Token 管理和管理面板。

核心组件:
    - providers: OAuth2 提供商实现（Google、GitHub 等）
    - services: 业务逻辑层（流程、账户、Token、会话、管理）
    - models: Pydantic 数据模型
    - repository: MongoDB 数据访问层
    - crypto: Token 加密存储
    - cache: Redis 缓存（State、Session）
    - integration: config_center 桥接
    - server: FastAPI Web 服务器
"""

from .errors import (
    OAuthAlreadyLinkedError,
    OAuthCannotUnlinkError,
    OAuthCodeExchangeError,
    OAuthCredentialNotFoundError,
    OAuthError,
    OAuthOnboardingError,
    OAuthProviderError,
    OAuthProviderNotRegisteredError,
    OAuthRefreshNotSupported,
    OAuthSessionError,
    OAuthStateError,
    OAuthTokenDecryptionError,
    OAuthTokenError,
    OAuthTokenRefreshError,
    OAuthUserInfoError,
)
from .models.enums import (
    OAuthActivityAction,
    OAuthActivityStatus,
    OAuthConnectionStatus,
    OAuthProvider,
)
from .models.profile import OAuthUserInfo, OnboardingData
from .providers import ProviderRegistry

__all__ = [
    # 枚举
    "OAuthProvider",
    "OAuthConnectionStatus",
    "OAuthActivityAction",
    "OAuthActivityStatus",
    # 数据模型
    "OAuthUserInfo",
    "OnboardingData",
    # 提供商注册表
    "ProviderRegistry",
    # 异常
    "OAuthError",
    "OAuthProviderError",
    "OAuthCodeExchangeError",
    "OAuthUserInfoError",
    "OAuthTokenError",
    "OAuthTokenRefreshError",
    "OAuthTokenDecryptionError",
    "OAuthRefreshNotSupported",
    "OAuthStateError",
    "OAuthCredentialNotFoundError",
    "OAuthProviderNotRegisteredError",
    "OAuthAlreadyLinkedError",
    "OAuthCannotUnlinkError",
    "OAuthSessionError",
    "OAuthOnboardingError",
]
