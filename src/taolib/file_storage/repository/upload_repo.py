"""上传会话 Repository。

提供上传会话的数据访问操作。
"""

from datetime import UTC, datetime

from taolib._base.repository import AsyncRepository
from taolib.file_storage.models.enums import UploadStatus
from taolib.file_storage.models.upload import UploadSessionDocument


class UploadSessionRepository(AsyncRepository[UploadSessionDocument]):
    """上传会话 Repository。"""

    def __init__(self, collection) -> None:
        super().__init__(collection, UploadSessionDocument)

    async def find_active_by_user(self, user_id: str) -> list[UploadSessionDocument]:
        """查找用户的活跃上传会话。"""
        cursor = self._collection.find(
            {
                "created_by": user_id,
                "status": {
                    "$in": [
                        UploadStatus.INITIATED,
                        UploadStatus.IN_PROGRESS,
                    ]
                },
            }
        )
        documents = await cursor.to_list(length=100)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(UploadSessionDocument(**doc))
        return results

    async def find_expired_sessions(
        self, before: datetime
    ) -> list[UploadSessionDocument]:
        """查找已过期的上传会话。"""
        cursor = self._collection.find(
            {
                "expires_at": {"$lte": before},
                "status": {
                    "$in": [
                        UploadStatus.INITIATED,
                        UploadStatus.IN_PROGRESS,
                    ]
                },
            }
        )
        documents = await cursor.to_list(length=1000)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(UploadSessionDocument(**doc))
        return results

    async def update_status(
        self, session_id: str, status: UploadStatus
    ) -> UploadSessionDocument | None:
        """更新上传状态。"""
        return await self.update(
            session_id,
            {"status": status, "updated_at": datetime.now(UTC)},
        )

    async def add_uploaded_chunk(
        self, session_id: str, chunk_index: int, bytes_count: int
    ) -> UploadSessionDocument | None:
        """添加已上传分片记录。"""
        result = await self._collection.find_one_and_update(
            {"_id": session_id},
            {
                "$addToSet": {"uploaded_chunks": chunk_index},
                "$inc": {"uploaded_bytes": bytes_count},
                "$set": {
                    "status": UploadStatus.IN_PROGRESS,
                    "updated_at": datetime.now(UTC),
                },
            },
            return_document=True,
        )
        if result is None:
            return None
        result["_id"] = str(result["_id"])
        return UploadSessionDocument(**result)

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("status")
        await self._collection.create_index("created_by")
        await self._collection.create_index("expires_at")
