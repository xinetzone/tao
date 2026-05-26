"""FastAPI 安全方案工厂。

提供 OAuth2 和 API Key 安全方案的工厂函数。
"""

from fastapi.security import APIKeyHeader, OAuth2PasswordBearer


def create_oauth2_scheme(
    token_url: str = "/api/v1/auth/token",
    auto_error: bool = False,
) -> OAuth2PasswordBearer:
    """创建 OAuth2 Password Bearer 安全方案。

    Args:
        token_url: 令牌获取端点 URL
        auto_error: 缺少令牌时是否自动返回 401（设为 False 以支持双通道认证）

    Returns:
        OAuth2PasswordBearer 实例
    """
    return OAuth2PasswordBearer(tokenUrl=token_url, auto_error=auto_error)


def create_api_key_header(
    name: str = "X-API-Key",
    auto_error: bool = False,
) -> APIKeyHeader:
    """创建 API Key Header 安全方案。

    Args:
        name: HTTP 头部名称
        auto_error: 缺少密钥时是否自动返回 401

    Returns:
        APIKeyHeader 实例
    """
    return APIKeyHeader(name=name, auto_error=auto_error)


