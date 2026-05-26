"""枚举定义模块。

定义 OAuth 系统中使用的所有枚举类型。
"""

from enum import StrEnum


class OAuthProvider(StrEnum):
    """OAuth 提供商枚举。"""

    GOOGLE = "google"
    GITHUB = "github"


class OAuthConnectionStatus(StrEnum):
    """OAuth 连接状态枚举。"""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    PENDING_ONBOARDING = "pending_onboarding"


class OAuthActivityAction(StrEnum):
    """OAuth 活动操作类型枚举。"""

    LOGIN = "oauth.login"
    LINK = "oauth.link"
    UNLINK = "oauth.unlink"
    TOKEN_REFRESH = "oauth.token_refresh"
    ONBOARDING_COMPLETE = "oauth.onboarding_complete"
    CREDENTIAL_CREATE = "oauth.credential.create"
    CREDENTIAL_UPDATE = "oauth.credential.update"
    CREDENTIAL_DELETE = "oauth.credential.delete"


class OAuthActivityStatus(StrEnum):
    """OAuth 活动状态枚举。"""

    SUCCESS = "success"
    FAILED = "failed"


