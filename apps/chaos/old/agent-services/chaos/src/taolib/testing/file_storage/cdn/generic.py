"""通用 CDN 提供商实现。

使用自定义 base URL 和 HMAC 签名。
"""

import hashlib
import hmac
import time


class GenericCDNProvider:
    """通用 CDN 提供商。

    支持自定义 base URL 和基于 HMAC 的 URL 签名。
    """

    def __init__(
        self,
        base_url: str,
        signing_key: str = "",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._signing_key = signing_key

    def generate_url(self, bucket: str, key: str) -> str:
        """生成 CDN 访问 URL。"""
        return f"{self._base_url}/{bucket}/{key}"

    def sign_url(self, url: str, expires_in: int = 3600) -> str:
        """生成 HMAC 签名 URL。"""
        if not self._signing_key:
            return url

        expires = int(time.time()) + expires_in
        message = f"{url}:{expires}"
        signature = hmac.new(
            self._signing_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        separator = "&" if "?" in url else "?"
        return f"{url}{separator}expires={expires}&signature={signature}"

    async def invalidate_paths(self, paths: list[str]) -> None:
        """通用 CDN 无内置刷新机制（留空实现）。"""

    async def invalidate_all(self) -> None:
        """通用 CDN 无内置全量刷新机制。"""
