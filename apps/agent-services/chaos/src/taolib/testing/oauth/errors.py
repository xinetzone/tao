"""OAuth 异常定义模块。

定义 OAuth 系统中使用的所有自定义异常。
"""


class OAuthError(Exception):
    """OAuth 基础异常。"""

    def __init__(self, message: str = "OAuth 操作失败") -> None:
        self.message = message
        super().__init__(self.message)


class OAuthProviderError(OAuthError):
    """OAuth 提供商返回错误。"""

    def __init__(self, message: str = "OAuth 提供商返回错误") -> None:
        super().__init__(message)


class OAuthCodeExchangeError(OAuthProviderError):
    """授权码交换失败。"""

    def __init__(self, message: str = "授权码交换失败") -> None:
        super().__init__(message)


class OAuthUserInfoError(OAuthProviderError):
    """获取用户信息失败。"""

    def __init__(self, message: str = "获取用户信息失败") -> None:
        super().__init__(message)


class OAuthTokenError(OAuthError):
    """Token 操作失败。"""

    def __init__(self, message: str = "Token 操作失败") -> None:
        super().__init__(message)


class OAuthTokenRefreshError(OAuthTokenError):
    """Token 刷新失败。"""

    def __init__(self, message: str = "Token 刷新失败") -> None:
        super().__init__(message)


class OAuthTokenDecryptionError(OAuthTokenError):
    """Token 解密失败。"""

    def __init__(self, message: str = "Token 解密失败") -> None:
        super().__init__(message)


class OAuthRefreshNotSupported(OAuthTokenError):
    """提供商不支持 Token 刷新。"""

    def __init__(self, message: str = "该提供商不支持 Token 刷新") -> None:
        super().__init__(message)


class OAuthStateError(OAuthError):
    """CSRF State 无效或已过期。"""

    def __init__(self, message: str = "无效或已过期的 OAuth State") -> None:
        super().__init__(message)


class OAuthCredentialNotFoundError(OAuthError):
    """未找到 OAuth 应用凭证。"""

    def __init__(self, message: str = "未找到 OAuth 应用凭证") -> None:
        super().__init__(message)


class OAuthProviderNotRegisteredError(OAuthError):
    """OAuth 提供商未注册。"""

    def __init__(self, message: str = "OAuth 提供商未注册") -> None:
        super().__init__(message)


class OAuthAlreadyLinkedError(OAuthError):
    """该提供商已关联到此账户。"""

    def __init__(self, message: str = "该提供商已关联到此账户") -> None:
        super().__init__(message)


class OAuthCannotUnlinkError(OAuthError):
    """无法解除关联（至少需要一种认证方式）。"""

    def __init__(self, message: str = "无法解除关联，至少需要保留一种认证方式") -> None:
        super().__init__(message)


class OAuthSessionError(OAuthError):
    """会话无效或已过期。"""

    def __init__(self, message: str = "会话无效或已过期") -> None:
        super().__init__(message)


class OAuthOnboardingError(OAuthError):
    """引导流程数据无效。"""

    def __init__(self, message: str = "引导流程数据无效") -> None:
        super().__init__(message)
