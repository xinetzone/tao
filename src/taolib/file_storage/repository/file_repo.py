"""文件元数据 Repository。

提供文件元数据的数据访问操作。
"""

from datetime import datetime
from typing import Any

from taolib._base.repository import AsyncRepository
from taolib.file_storage.models.enums import FileStatus, MediaType
from taolib.file_storage.models.file import FileMetadataDocument


class FileRepository(AsyncRepository[FileMetadataDocument]):
    """文件元数据 Repository。"""

    def __init__(self, collection) -> None:
        super().__init__(collection, FileMetadataDocument)

    async def find_by_bucket(
        self,
        bucket_id: str,
        prefix: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FileMetadataDocument]:
        """查找桶内文件。"""
        filters: dict[str, Any] = {
            "bucket_id": bucket_id,
            "status": {"$ne": FileStatus.DELETED},
        }
        if prefix:
            filters["object_key"] = {"$regex": f"^{prefix}"}
        cursor = (
            self._collection.find(filters)
            .skip(skip)
            .limit(limit)
            .sort([("created_at", -1)])
        )
        documents = await cursor.to_list(length=limit)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(FileMetadataDocument(**doc))
        return results

    async def find_by_object_key(
        self, bucket_id: str, object_key: str
    ) -> FileMetadataDocument | None:
        """根据桶 ID 和对象键查找文件。"""
        document = await self._collection.find_one(
            {"bucket_id": bucket_id, "object_key": object_key}
        )
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return FileMetadataDocument(**document)

    async def find_expired_files(self, before: datetime) -> list[FileMetadataDocument]:
        """查找已过期文件。"""
        cursor = self._collection.find(
            {
                "expires_at": {"$ne": None, "$lte": before},
                "status": FileStatus.ACTIVE,
            }
        )
        documents = await cursor.to_list(length=1000)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(FileMetadataDocument(**doc))
        return results

    async def find_by_tags(
        self, tags: list[str], bucket_id: str | None = None
    ) -> list[FileMetadataDocument]:
        """根据标签查找文件。"""
        filters: dict[str, Any] = {
            "tags": {"$all": tags},
            "status": {"$ne": FileStatus.DELETED},
        }
        if bucket_id:
            filters["bucket_id"] = bucket_id
        cursor = self._collection.find(filters)
        documents = await cursor.to_list(length=100)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(FileMetadataDocument(**doc))
        return results

    async def find_by_media_type(
        self, media_type: MediaType, bucket_id: str | None = None
    ) -> list[FileMetadataDocument]:
        """根据媒体类型查找文件。"""
        filters: dict[str, Any] = {
            "media_type": media_type,
            "status": {"$ne": FileStatus.DELETED},
        }
        if bucket_id:
            filters["bucket_id"] = bucket_id
        cursor = self._collection.find(filters)
        documents = await cursor.to_list(length=100)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(FileMetadataDocument(**doc))
        return results

    async def update_status(
        self, file_id: str, status: FileStatus
    ) -> FileMetadataDocument | None:
        """更新文件状态。"""
        return await self.update(file_id, {"status": status})

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index(
            [("bucket_id", 1), ("object_key", 1)], unique=True
        )
        await self._collection.create_index("status")
        await self._collection.create_index("tags")
        await self._collection.create_index("media_type")
        await self._collection.create_index("expires_at")
        await self._collection.create_index([("bucket_id", 1), ("created_at", -1)])
