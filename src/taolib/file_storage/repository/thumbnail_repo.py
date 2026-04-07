"""缩略图 Repository。

提供缩略图记录的数据访问操作。
"""

from taolib._base.repository import AsyncRepository
from taolib.file_storage.models.enums import ThumbnailSize
from taolib.file_storage.models.thumbnail import ThumbnailDocument


class ThumbnailRepository(AsyncRepository[ThumbnailDocument]):
    """缩略图 Repository。"""

    def __init__(self, collection) -> None:
        super().__init__(collection, ThumbnailDocument)

    async def find_by_file(self, file_id: str) -> list[ThumbnailDocument]:
        """查找文件的所有缩略图。"""
        cursor = self._collection.find({"file_id": file_id})
        documents = await cursor.to_list(length=10)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(ThumbnailDocument(**doc))
        return results

    async def find_by_file_and_size(
        self, file_id: str, size: ThumbnailSize
    ) -> ThumbnailDocument | None:
        """查找指定文件的指定规格缩略图。"""
        document = await self._collection.find_one({"file_id": file_id, "size": size})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return ThumbnailDocument(**document)

    async def delete_by_file(self, file_id: str) -> int:
        """删除文件的所有缩略图记录。"""
        result = await self._collection.delete_many({"file_id": file_id})
        return result.deleted_count

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index([("file_id", 1), ("size", 1)], unique=True)
        await self._collection.create_index("file_id")
