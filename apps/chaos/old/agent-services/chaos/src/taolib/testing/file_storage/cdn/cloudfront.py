"""AWS CloudFront CDN 提供商实现。

提供 CloudFront URL 生成和缓存刷新功能。
"""

import hashlib
import hmac
import time


class CloudFrontCDNProvider:
    """AWS CloudFront CDN 提供商。"""

    def __init__(
        self,
        distribution_domain: str,
        key_pair_id: str = "",
        private_key: str = "",
    ) -> None:
        self._domain = distribution_domain.rstrip("/")
        self._key_pair_id = key_pair_id
        self._private_key = private_key

    def generate_url(self, bucket: str, key: str) -> str:
        """生成 CloudFront 访问 URL。"""
        return f"https://{self._domain}/{key}"

    def sign_url(self, url: str, expires_in: int = 3600) -> str:
        """生成 CloudFront 签名 URL。

        注意：完整的 CloudFront 签名需要 RSA 私钥。
        此处提供 HMAC 简化签名方案。
        """
        if not self._private_key:
            return url

        expires = int(time.time()) + expires_in
        message = f"{url}:{expires}"
        signature = hmac.new(
            self._private_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        separator = "&" if "?" in url else "?"
        return (
            f"{url}{separator}Expires={expires}"
            f"&Signature={signature}"
            f"&Key-Pair-Id={self._key_pair_id}"
        )

    async def invalidate_paths(self, paths: list[str]) -> None:
        """CloudFront 缓存刷新。

        注意：完整实现需要 boto3 调用 create_invalidation API。
        此处为占位实现。
        """

    async def invalidate_all(self) -> None:
        """CloudFront 全量缓存刷新。"""
        await self.invalidate_paths(["/*"])
