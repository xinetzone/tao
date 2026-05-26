"""泛型 Repository 基类模块。

提供异步 MongoDB Repository 的通用 CRUD 操作实现。
"""

from abc import ABC
from typing import Any, Generic, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class AsyncRepository(ABC, Generic[T]):
    """异步 Repository 基类。"""

    def __init__(
        self, collection: AsyncIOMotorCollection, model_class: type[T]
    ) -> None:
        """初始化 Repository。

        Args:
            collection: MongoDB 集合对象
            model_class: Pydantic 模型类
        """
        self._collection = collection
        self._model_class = model_class

    async def create(self, document: dict[str, Any]) -> T:
        """创建文档。

        Args:
            document: 文档数据字典

        Returns:
            创建的文档对应的 Pydantic 模型实例
        """
        result = await self._collection.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return self._model_class(**document)

    async def get_by_id(self, doc_id: str) -> T | None:
        """根据 ID 获取文档。

        Args:
            doc_id: 文档 ID

        Returns:
            Pydantic 模型实例，如果不存在则返回 None
        """
        document = await self._collection.find_one({"_id": doc_id})
        if document is None:
            return None
        document["_id"] = str(document["_id"])
        return self._model_class(**document)

    async def update(self, doc_id: str, updates: dict[str, Any]) -> T | None:
        """更新文档。

        Args:
            doc_id: 文档 ID
            updates: 更新字段字典

        Returns:
            更新后的 Pydantic 模型实例，如果不存在则返回 None
        """
        result = await self._collection.find_one_and_update(
            {"_id": doc_id},
            {"$set": updates},
            return_document=True,
        )
        if result is None:
            return None
        result["_id"] = str(result["_id"])
        return self._model_class(**result)

    async def delete(self, doc_id: str) -> bool:
        """删除文档。

        Args:
            doc_id: 文档 ID

        Returns:
            是否删除成功
        """
        result = await self._collection.delete_one({"_id": doc_id})
        return result.deleted_count > 0

    async def list(
        self,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 100,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[T]:
        """查询文档列表。

        Args:
            filters: 过滤条件
            skip: 跳过记录数
            limit: 限制记录数
            sort: 排序条件

        Returns:
            Pydantic 模型实例列表
        """
        query_filters = filters or {}
        cursor = self._collection.find(query_filters).skip(skip).limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        documents = await cursor.to_list(length=limit)
        results = []
        for doc in documents:
            doc["_id"] = str(doc["_id"])
            results.append(self._model_class(**doc))
        return results

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """统计文档数量。

        Args:
            filters: 过滤条件

        Returns:
            符合条件的文档数量
        """
        return await self._collection.count_documents(filters or {})


