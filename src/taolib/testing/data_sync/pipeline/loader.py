"""MongoDB 数据加载器。

实现批量 upsert 操作。
"""

import logging
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from taolib.testing.data_sync.pipeline.protocols import LoadResult

logger = logging.getLogger(__name__)


class MongoLoader:
    """MongoDB 数据加载器。

    使用 bulk_write + ReplaceOne(upsert=True) 实现高效加载。
    """

    async def load(
        self,
        target_collection: AsyncIOMotorCollection,
        documents: list[dict[str, Any]],
    ) -> LoadResult:
        """批量加载文档到目标集合。

        Args:
            target_collection: 目标集合
            documents: 文档列表

        Returns:
            加载结果
        """
        if not documents:
            return LoadResult(inserted=0, updated=0, failed=0)

        operations = [
            ReplaceOne({"_id": doc["_id"]}, doc, upsert=True) for doc in documents
        ]

        try:
            result = await target_collection.bulk_write(operations)
            logger.debug(
                "批量加载完成: inserted=%d, modified=%d",
                result.inserted_count,
                result.modified_count,
            )
            return LoadResult(
                inserted=result.inserted_count,
                updated=result.modified_count,
                failed=0,
            )
        except BulkWriteError as e:
            # 批量写入部分失败 - 记录失败情况
            logger.warning("批量写入部分失败: %s", e)
            details = e.details
            inserted = details.get("nInserted", 0)
            modified = details.get("nModified", 0)
            failed = len(documents) - inserted - modified

            failures = []
            for err in details.get("writeErrors", []):
                failures.append(
                    {
                        "error_type": "BulkWriteError",
                        "error_message": err.get("errmsg", "Unknown error"),
                        "document_id": err.get("op", {}).get("_id", "unknown"),
                    }
                )

            return LoadResult(
                inserted=inserted,
                updated=modified,
                failed=failed,
                failures=failures,
            )
        except Exception as e:
            # 完全失败
            logger.error("批量写入完全失败: %s", e)
            return LoadResult(
                inserted=0,
                updated=0,
                failed=len(documents),
                failures=[
                    {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "document_id": "batch_error",
                    }
                ],
            )


