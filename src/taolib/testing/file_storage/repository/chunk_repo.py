"""分片记录 Repository。

提供分片记录的数据访问操作。
"""

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.file_storage.models.upload import ChunkRecord


class ChunkRepository(AsyncRepository[ChunkRecord]):
    """分片记录 Repository。"""

    def __init__(self, collection) -> None:
        super().__init__(collection, ChunkRecord)

    async def find_by_session(self, session_id: str) -> list[ChunkRecord]:
        """查找会话的所有分片。"""
        cursor = self._collection.find({"session_id": session_id}).sort(
            [("chunk_index", 1)]
        )
        documents = await cursor.to_list(length=10000)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(ChunkRecord(**doc))
        return results

    async def find_by_session_and_index(
        self, session_id: str, chunk_index: int
    ) -> ChunkRecord | None:
        """查找指定分片。"""
        document = await self._collection.find_one(
            {"session_id": session_id, "chunk_index": chunk_index}
        )
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return ChunkRecord(**document)

    async def count_by_session(self, session_id: str) -> int:
        """统计会话的分片数量。"""
        return await self._collection.count_documents({"session_id": session_id})

    async def delete_by_session(self, session_id: str) -> int:
        """删除会话的所有分片记录。"""
        result = await self._collection.delete_many({"session_id": session_id})
        return result.deleted_count

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index(
            [("session_id", 1), ("chunk_index", 1)], unique=True
        )
        await self._collection.create_index("session_id")


