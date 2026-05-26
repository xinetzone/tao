"""MongoDB 数据提取器。

实现基于时间戳的增量/全量数据提取。
"""

import logging
from collections.abc import AsyncIterator
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection

from taolib.testing.data_sync.models.checkpoint import SyncCheckpoint

logger = logging.getLogger(__name__)


class MongoExtractor:
    """MongoDB 数据提取器。

    支持增量（基于时间戳）和全量两种提取模式。
    """

    def __init__(self, batch_size: int = 1000) -> None:
        """初始化提取器。

        Args:
            batch_size: 每批文档数量
        """
        self._batch_size = batch_size

    async def extract(
        self,
        source_collection: AsyncIOMotorCollection,
        checkpoint: SyncCheckpoint | None = None,
        filter_query: dict[str, Any] | None = None,
        batch_size: int | None = None,
    ) -> AsyncIterator[list[dict[str, Any]]]:
        """分批提取源数据。

        Args:
            source_collection: 源集合
            checkpoint: 检查点（增量同步时使用）
            filter_query: 额外过滤条件
            batch_size: 批次大小（覆盖构造函数值）

        Yields:
            文档批次列表
        """
        effective_batch_size = batch_size or self._batch_size
        query = dict(filter_query) if filter_query else {}

        # 增量模式：添加时间戳过滤
        if checkpoint and checkpoint.last_synced_timestamp:
            query["updated_at"] = {"$gt": checkpoint.last_synced_timestamp}

        # 排序：按 updated_at, _id 确保顺序一致性
        cursor = (
            source_collection.find(query)
            .sort([("updated_at", 1), ("_id", 1)])
            .batch_size(effective_batch_size)
        )

        batch: list[dict[str, Any]] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # ObjectId → str
            batch.append(doc)

            if len(batch) >= effective_batch_size:
                logger.debug("提取批次: %d 条文档", len(batch))
                yield batch
                batch = []

        if batch:
            logger.debug("提取最后批次: %d 条文档", len(batch))
            yield batch


