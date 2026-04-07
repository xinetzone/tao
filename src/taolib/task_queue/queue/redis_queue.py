"""Redis 任务队列。

基于 Redis 的任务队列实现，支持优先级、重试调度和实时统计。
"""

import time
from typing import Any

from redis.asyncio import Redis

from taolib.task_queue.models.enums import TaskPriority


class RedisTaskQueue:
    """Redis 任务队列。

    使用 Redis List 实现优先级队列，Sorted Set 实现重试调度。

    Redis 键结构：
        {prefix}:queue:high     - LIST: 高优先级待处理任务
        {prefix}:queue:normal   - LIST: 普通优先级待处理任务
        {prefix}:queue:low      - LIST: 低优先级待处理任务
        {prefix}:running        - SET: 运行中任务 ID
        {prefix}:completed      - LIST: 最近完成的任务 ID（上限 1000）
        {prefix}:failed         - SET: 失败任务 ID
        {prefix}:retry          - ZSET: 重试调度（score = retry_at 时间戳）
        {prefix}:task:{id}      - HASH: 任务元数据缓存
        {prefix}:stats          - HASH: 全局计数器
    """

    def __init__(
        self,
        redis: Redis,
        key_prefix: str = "tq",
    ) -> None:
        """初始化。

        Args:
            redis: Redis 异步客户端
            key_prefix: Redis 键前缀
        """
        self._redis = redis
        self._prefix = key_prefix

    def _key(self, suffix: str) -> str:
        """生成 Redis 键。"""
        return f"{self._prefix}:{suffix}"

    @property
    def _queue_keys(self) -> list[str]:
        """优先级队列键列表（高 → 普通 → 低）。"""
        return [
            self._key(f"queue:{TaskPriority.HIGH}"),
            self._key(f"queue:{TaskPriority.NORMAL}"),
            self._key(f"queue:{TaskPriority.LOW}"),
        ]

    async def enqueue(
        self,
        task_id: str,
        priority: TaskPriority,
        task_meta: dict[str, str],
    ) -> None:
        """将任务加入队列。

        Args:
            task_id: 任务 ID
            priority: 任务优先级
            task_meta: 任务元数据（用于 Redis 缓存）
        """
        queue_key = self._key(f"queue:{priority}")
        task_hash_key = self._key(f"task:{task_id}")
        stats_key = self._key("stats")

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.hset(task_hash_key, mapping=task_meta)
            pipe.lpush(queue_key, task_id)
            pipe.hincrby(stats_key, "total_submitted", 1)
            await pipe.execute()

    async def dequeue(self, timeout: float = 5.0) -> str | None:
        """从队列中取出一个任务（按优先级顺序）。

        使用 BRPOP 阻塞等待，优先消费高优先级队列。

        Args:
            timeout: 阻塞等待超时时间（秒）

        Returns:
            任务 ID，超时返回 None
        """
        result = await self._redis.brpop(self._queue_keys, timeout=int(timeout))
        if result is None:
            return None

        # result = (queue_key, task_id)
        task_id = result[1]
        if isinstance(task_id, bytes):
            task_id = task_id.decode("utf-8")

        # 加入运行中集合
        await self._redis.sadd(self._key("running"), task_id)
        return task_id

    async def ack(self, task_id: str) -> None:
        """确认任务完成（成功）。

        Args:
            task_id: 任务 ID
        """
        running_key = self._key("running")
        completed_key = self._key("completed")
        failed_key = self._key("failed")
        stats_key = self._key("stats")
        task_hash_key = self._key(f"task:{task_id}")

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.srem(running_key, task_id)
            pipe.srem(failed_key, task_id)  # 重试成功时清除失败记录
            pipe.lpush(completed_key, task_id)
            pipe.ltrim(completed_key, 0, 999)  # 保留最近 1000 条
            pipe.hincrby(stats_key, "total_completed", 1)
            pipe.delete(task_hash_key)
            await pipe.execute()

    async def nack(
        self,
        task_id: str,
        *,
        schedule_retry: bool,
        retry_at: float | None = None,
    ) -> None:
        """标记任务失败。

        Args:
            task_id: 任务 ID
            schedule_retry: 是否调度重试
            retry_at: 重试时间戳（仅 schedule_retry=True 时有效）
        """
        running_key = self._key("running")
        stats_key = self._key("stats")

        if schedule_retry and retry_at is not None:
            retry_key = self._key("retry")
            async with self._redis.pipeline(transaction=True) as pipe:
                pipe.srem(running_key, task_id)
                pipe.zadd(retry_key, {task_id: retry_at})
                pipe.hincrby(stats_key, "total_retried", 1)
                await pipe.execute()
        else:
            failed_key = self._key("failed")
            async with self._redis.pipeline(transaction=True) as pipe:
                pipe.srem(running_key, task_id)
                pipe.sadd(failed_key, task_id)
                pipe.hincrby(stats_key, "total_failed", 1)
                await pipe.execute()

    async def poll_retries(self) -> list[str]:
        """轮询到期的重试任务并重新入队。

        Returns:
            重新入队的任务 ID 列表
        """
        retry_key = self._key("retry")
        now = time.time()

        # 获取到期的任务
        task_ids = await self._redis.zrangebyscore(retry_key, 0, now)
        if not task_ids:
            return []

        re_enqueued: list[str] = []
        for raw_id in task_ids:
            task_id = raw_id.decode("utf-8") if isinstance(raw_id, bytes) else raw_id

            # 从重试集合中移除
            removed = await self._redis.zrem(retry_key, task_id)
            if not removed:
                continue

            # 获取任务优先级
            task_hash_key = self._key(f"task:{task_id}")
            priority = await self._redis.hget(task_hash_key, "priority")
            if priority is None:
                priority = TaskPriority.NORMAL
            elif isinstance(priority, bytes):
                priority = priority.decode("utf-8")

            # 重新入队
            queue_key = self._key(f"queue:{priority}")
            await self._redis.lpush(queue_key, task_id)
            re_enqueued.append(task_id)

        return re_enqueued

    async def get_task_meta(self, task_id: str) -> dict[str, str] | None:
        """获取任务元数据缓存。

        Args:
            task_id: 任务 ID

        Returns:
            任务元数据字典，不存在返回 None
        """
        task_hash_key = self._key(f"task:{task_id}")
        data = await self._redis.hgetall(task_hash_key)
        if not data:
            return None
        return {
            (k.decode("utf-8") if isinstance(k, bytes) else k): (
                v.decode("utf-8") if isinstance(v, bytes) else v
            )
            for k, v in data.items()
        }

    async def set_task_meta(self, task_id: str, meta: dict[str, str]) -> None:
        """设置任务元数据缓存。

        Args:
            task_id: 任务 ID
            meta: 元数据字典
        """
        task_hash_key = self._key(f"task:{task_id}")
        await self._redis.hset(task_hash_key, mapping=meta)

    async def get_stats(self) -> dict[str, Any]:
        """获取队列统计信息。

        Returns:
            包含各项统计指标的字典
        """
        stats_key = self._key("stats")
        running_key = self._key("running")
        failed_key = self._key("failed")
        completed_key = self._key("completed")
        retry_key = self._key("retry")

        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.hgetall(stats_key)
            pipe.llen(self._key(f"queue:{TaskPriority.HIGH}"))
            pipe.llen(self._key(f"queue:{TaskPriority.NORMAL}"))
            pipe.llen(self._key(f"queue:{TaskPriority.LOW}"))
            pipe.scard(running_key)
            pipe.scard(failed_key)
            pipe.llen(completed_key)
            pipe.zcard(retry_key)
            results = await pipe.execute()

        raw_stats = results[0]
        stats: dict[str, str] = {}
        if raw_stats:
            stats = {
                (k.decode("utf-8") if isinstance(k, bytes) else k): (
                    v.decode("utf-8") if isinstance(v, bytes) else v
                )
                for k, v in raw_stats.items()
            }

        return {
            "total_submitted": int(stats.get("total_submitted", 0)),
            "total_completed": int(stats.get("total_completed", 0)),
            "total_failed": int(stats.get("total_failed", 0)),
            "total_retried": int(stats.get("total_retried", 0)),
            "queue_high": results[1],
            "queue_normal": results[2],
            "queue_low": results[3],
            "running": results[4],
            "failed": results[5],
            "completed_recent": results[6],
            "retrying": results[7],
        }

    async def get_queue_lengths(self) -> dict[str, int]:
        """获取各优先级队列长度。

        Returns:
            各队列长度字典
        """
        async with self._redis.pipeline(transaction=False) as pipe:
            pipe.llen(self._key(f"queue:{TaskPriority.HIGH}"))
            pipe.llen(self._key(f"queue:{TaskPriority.NORMAL}"))
            pipe.llen(self._key(f"queue:{TaskPriority.LOW}"))
            results = await pipe.execute()

        return {
            "high": results[0],
            "normal": results[1],
            "low": results[2],
        }

    async def get_running_task_ids(self) -> set[str]:
        """获取运行中任务 ID 集合。

        Returns:
            任务 ID 集合
        """
        raw = await self._redis.smembers(self._key("running"))
        return {m.decode("utf-8") if isinstance(m, bytes) else m for m in raw}

    async def remove_from_running(self, task_id: str) -> None:
        """从运行中集合移除任务。

        Args:
            task_id: 任务 ID
        """
        await self._redis.srem(self._key("running"), task_id)

    async def remove_from_failed(self, task_id: str) -> None:
        """从失败集合移除任务。

        Args:
            task_id: 任务 ID
        """
        await self._redis.srem(self._key("failed"), task_id)
