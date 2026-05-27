"""事件发布器。

通过 Redis PubSub 发布文件存储事件。
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class StorageEventPublisher:
    """文件存储事件发布器。"""

    CHANNEL_PREFIX = "storage"

    def __init__(self, redis_client: Any | None = None) -> None:
        self._redis = redis_client

    async def publish(self, event_type: str, event_data: dict) -> None:
        """发布事件。

        Args:
            event_type: 事件类型（如 'file.uploaded'）
            event_data: 事件数据字典
        """
        if self._redis is None:
            logger.debug("Redis 未配置，跳过事件发布: %s", event_type)
            return

        channel = f"{self.CHANNEL_PREFIX}:{event_type}"
        message = json.dumps(event_data, default=str)
        try:
            await self._redis.publish(channel, message)
        except Exception:
            logger.exception("事件发布失败: %s", event_type)

    async def publish_file_uploaded(self, event) -> None:
        """发布文件上传事件。"""
        await self.publish("file.uploaded", event.to_dict())

    async def publish_file_deleted(self, event) -> None:
        """发布文件删除事件。"""
        await self.publish("file.deleted", event.to_dict())

    async def publish_upload_completed(self, event) -> None:
        """发布上传完成事件。"""
        await self.publish("upload.completed", event.to_dict())

    async def publish_bucket_created(self, event) -> None:
        """发布存储桶创建事件。"""
        await self.publish("bucket.created", event.to_dict())
