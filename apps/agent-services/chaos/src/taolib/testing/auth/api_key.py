"""API 密钥认证模块。

提供 API 密钥查找的 Protocol 接口和静态配置实现。
"""

from typing import Protocol, runtime_checkable

from .models import AuthenticatedUser


@runtime_checkable
class APIKeyLookupProtocol(Protocol):
    """API 密钥查找 Protocol。

    定义 API 密钥认证的标准接口，支持多种存储后端。
    """

    async def lookup(self, api_key: str) -> AuthenticatedUser | None:
        """根据 API 密钥查找对应的用户信息。

        Args:
            api_key: API 密钥字符串

        Returns:
            如果密钥有效返回 AuthenticatedUser，否则返回 None
        """
        ...


class StaticAPIKeyLookup:
    """基于静态配置的 API 密钥查找。

    从构造时传入的字典中查找 API 密钥，适合小规模部署
    或配置文件管理的固定密钥。

    Args:
        keys: API 密钥到用户信息的映射
    """

    def __init__(self, keys: dict[str, AuthenticatedUser]) -> None:
        self._keys = dict(keys)

    async def lookup(self, api_key: str) -> AuthenticatedUser | None:
        """从静态配置中查找 API 密钥。"""
        return self._keys.get(api_key)
