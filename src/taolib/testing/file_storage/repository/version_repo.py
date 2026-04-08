"""文件版本 Repository。

提供文件版本的数据访问操作。
"""

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.file_storage.models.version import FileVersionDocument


class FileVersionRepository(AsyncRepository[FileVersionDocument]):
    """文件版本 Repository。"""

    def __init__(self, collection) -> None:
        super().__init__(collection, FileVersionDocument)

    async def find_by_file(
        self,
        file_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[FileVersionDocument]:
        """查找文件的版本历史（按版本号降序）。"""
        cursor = (
            self._collection.find({"file_id": file_id})
            .sort([("version_number", -1)])
            .skip(skip)
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(FileVersionDocument(**doc))
        return results

    async def find_latest(self, file_id: str) -> FileVersionDocument | None:
        """获取最新版本。"""
        document = await self._collection.find_one(
            {"file_id": file_id},
            sort=[("version_number", -1)],
        )
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return FileVersionDocument(**document)

    async def count_by_file(self, file_id: str) -> int:
        """统计文件版本数量。"""
        return await self._collection.count_documents({"file_id": file_id})

    async def delete_oldest(self, file_id: str, keep_count: int) -> int:
        """删除最旧的版本，保留指定数量。"""
        versions = await self.find_by_file(file_id, skip=keep_count, limit=1000)
        if not versions:
            return 0
        ids = [v.id for v in versions]
        result = await self._collection.delete_many({"_id": {"$in": ids}})
        return result.deleted_count

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index(
            [("file_id", 1), ("version_number", 1)], unique=True
        )
        await self._collection.create_index("file_id")


