"""存储桶 Repository。

提供存储桶的数据访问操作。
"""

from datetime import UTC, datetime

from taolib.testing._base.repository import AsyncRepository
from taolib.testing.file_storage.models.bucket import BucketDocument


class BucketRepository(AsyncRepository[BucketDocument]):
    """存储桶 Repository。"""

    def __init__(self, collection) -> None:
        super().__init__(collection, BucketDocument)

    async def find_by_name(self, name: str) -> BucketDocument | None:
        """根据名称查找存储桶。"""
        document = await self._collection.find_one({"name": name})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return BucketDocument(**document)

    async def find_by_tags(self, tags: list[str]) -> list[BucketDocument]:
        """根据标签查找存储桶。"""
        cursor = self._collection.find({"tags": {"$all": tags}})
        documents = await cursor.to_list(length=100)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(BucketDocument(**doc))
        return results

    async def increment_file_count(
        self,
        bucket_id: str,
        count_delta: int = 1,
        size_delta: int = 0,
    ) -> BucketDocument | None:
        """增量更新文件计数和大小。"""
        result = await self._collection.find_one_and_update(
            {"_id": bucket_id},
            {
                "$inc": {
                    "file_count": count_delta,
                    "total_size_bytes": size_delta,
                },
                "$set": {"updated_at": datetime.now(UTC)},
            },
            return_document=True,
        )
        if result is None:
            return None
        result["_id"] = str(result["_id"])
        return BucketDocument(**result)

    async def create_indexes(self) -> None:
        """创建索引。"""
        await self._collection.create_index("name", unique=True)
        await self._collection.create_index("tags")
        await self._collection.create_index("storage_class")


