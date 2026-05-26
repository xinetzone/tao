"""认证异常层次结构。

定义所有认证相关的异常类型，提供清晰的错误分类和描述性消息。
"""


class AuthError(Exception):
    """所有认证错误的基类。"""

    def __init__(self, message: str = "认证错误") -> None:
        self.message = message
        super().__init__(message)


class TokenExpiredError(AuthError):
    """令牌已过期。"""

    def __init__(self, message: str = "令牌已过期，请刷新") -> None:
        super().__init__(message)


class TokenInvalidError(AuthError):
    """令牌无效（解码失败或签名不匹配）。"""

    def __init__(
        self,
        message: str = "无效的认证令牌",
        detail: str | None = None,
    ) -> None:
        self.detail = detail
        super().__init__(message)


class TokenBlacklistedError(AuthError):
    """令牌已被吊销（在黑名单中）。"""

    def __init__(self, message: str = "令牌已被吊销") -> None:
        super().__init__(message)


class InsufficientPermissionError(AuthError):
    """权限不足。"""

    def __init__(self, message: str = "权限不足") -> None:
        super().__init__(message)


class APIKeyInvalidError(AuthError):
    """API 密钥无效或未找到。"""

    def __init__(self, message: str = "无效的 API 密钥") -> None:
        super().__init__(message)


