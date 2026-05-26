"""CDN 提供商协议定义。

定义 CDNProviderProtocol 接口。
"""

from typing import Protocol


class CDNProviderProtocol(Protocol):
    """CDN 提供商协议。"""

    def generate_url(self, bucket: str, key: str) -> str:
        """生成 CDN 访问 URL。"""
        ...

    def sign_url(self, url: str, expires_in: int = 3600) -> str:
        """生成签名 URL。"""
        ...

    async def invalidate_paths(self, paths: list[str]) -> None:
        """刷新 CDN 缓存（指定路径）。"""
        ...

    async def invalidate_all(self) -> None:
        """刷新 CDN 全部缓存。"""
        ...


