"""访问控制服务。

提供签名 URL 生成与验证、访问控制检查。
"""

import hashlib
import hmac
import time

from taolib.testing.file_storage.cdn.protocols import CDNProviderProtocol
from taolib.testing.file_storage.errors import (
    FileNotFoundError_,
)
from taolib.testing.file_storage.models.enums import AccessLevel
from taolib.testing.file_storage.repository.file_repo import FileRepository
from taolib.testing.file_storage.storage.protocols import StorageBackendProtocol


class AccessService:
    """访问控制服务。"""

    def __init__(
        self,
        file_repo: FileRepository,
        storage_backend: StorageBackendProtocol,
        cdn_provider: CDNProviderProtocol | None = None,
        signed_url_secret: str = "",
    ) -> None:
        self._file_repo = file_repo
        self._storage_backend = storage_backend
        self._cdn_provider = cdn_provider
        self._secret = signed_url_secret

    async def generate_signed_url(
        self,
        file_id: str,
        expires_in: int = 3600,
        method: str = "GET",
    ) -> str:
        """生成签名 URL。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")

        # 优先使用 CDN
        if self._cdn_provider is not None:
            url = self._cdn_provider.generate_url(file.bucket_id, file.object_key)
            return self._cdn_provider.sign_url(url, expires_in)

        # 回退到后端预签名 URL
        return await self._storage_backend.generate_presigned_url(
            file.bucket_id, file.object_key, expires_in, method
        )

    def generate_token(
        self, file_id: str, expires_in: int = 3600
    ) -> dict[str, str | int]:
        """生成签名 token。"""
        expires = int(time.time()) + expires_in
        message = f"{file_id}:{expires}"
        signature = hmac.new(
            self._secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return {
            "file_id": file_id,
            "expires": expires,
            "signature": signature,
        }

    def validate_token(self, file_id: str, expires: int, signature: str) -> bool:
        """验证签名 token。"""
        if time.time() > expires:
            return False
        message = f"{file_id}:{expires}"
        expected = hmac.new(
            self._secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    async def check_access(
        self,
        file_id: str,
        user_id: str | None = None,
        action: str = "read",
    ) -> bool:
        """检查访问权限。"""
        file = await self._file_repo.get_by_id(file_id)
        if file is None:
            raise FileNotFoundError_(f"文件不存在: {file_id}")

        if file.access_level == AccessLevel.PUBLIC:
            return True

        if file.access_level == AccessLevel.PRIVATE:
            return user_id is not None and file.created_by == user_id

        # SIGNED_URL 级别需要额外的 token 验证
        return False


