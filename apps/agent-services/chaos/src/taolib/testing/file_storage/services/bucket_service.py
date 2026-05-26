"""存储桶服务。

提供存储桶管理的业务逻辑。
"""

from datetime import UTC, datetime

from taolib.testing.file_storage.errors import (
    BucketNotEmptyError,
    BucketNotFoundError,
    DuplicateObjectError,
)
from taolib.testing.file_storage.models.bucket import (
    BucketCreate,
    BucketResponse,
    BucketUpdate,
)
from taolib.testing.file_storage.repository.bucket_repo import BucketRepository
from taolib.testing.file_storage.storage.protocols import StorageBackendProtocol


class BucketService:
    """存储桶管理服务。"""

    def __init__(
        self,
        bucket_repo: BucketRepository,
        storage_backend: StorageBackendProtocol,
    ) -> None:
        self._bucket_repo = bucket_repo
        self._storage_backend = storage_backend

    async def create_bucket(
        self, data: BucketCreate, user_id: str = "system"
    ) -> BucketResponse:
        """创建存储桶。"""
        existing = await self._bucket_repo.find_by_name(data.name)
        if existing is not None:
            raise DuplicateObjectError(f"存储桶已存在: {data.name}")

        # 在后端创建桶
        await self._storage_backend.create_bucket(data.name)

        now = datetime.now(UTC)
        doc = {
            "_id": data.name,
            **data.model_dump(),
            "file_count": 0,
            "total_size_bytes": 0,
            "created_by": user_id,
            "created_at": now,
            "updated_at": now,
        }
        bucket = await self._bucket_repo.create(doc)
        return bucket.to_response()

    async def get_bucket(self, bucket_id: str) -> BucketResponse | None:
        """获取存储桶详情。"""
        bucket = await self._bucket_repo.get_by_id(bucket_id)
        if bucket is None:
            return None
        return bucket.to_response()

    async def update_bucket(
        self,
        bucket_id: str,
        data: BucketUpdate,
        user_id: str = "system",
    ) -> BucketResponse | None:
        """更新存储桶配置。"""
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return await self.get_bucket(bucket_id)
        updates["updated_at"] = datetime.now(UTC)
        bucket = await self._bucket_repo.update(bucket_id, updates)
        if bucket is None:
            return None
        return bucket.to_response()

    async def delete_bucket(self, bucket_id: str, force: bool = False) -> bool:
        """删除存储桶。"""
        bucket = await self._bucket_repo.get_by_id(bucket_id)
        if bucket is None:
            raise BucketNotFoundError(f"存储桶不存在: {bucket_id}")

        if bucket.file_count > 0 and not force:
            raise BucketNotEmptyError(
                f"存储桶 {bucket_id} 包含 {bucket.file_count} 个文件，"
                "请先删除所有文件或使用 force=True"
            )

        await self._storage_backend.delete_bucket(bucket_id)
        return await self._bucket_repo.delete(bucket_id)

    async def list_buckets(
        self, skip: int = 0, limit: int = 100
    ) -> list[BucketResponse]:
        """列出所有存储桶。"""
        buckets = await self._bucket_repo.list(skip=skip, limit=limit)
        return [b.to_response() for b in buckets]


