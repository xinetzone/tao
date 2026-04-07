"""Redis 任务队列测试。

使用 mock Redis 客户端测试 RedisTaskQueue 的入队、出队、确认和统计操作。
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.task_queue.models.enums import TaskPriority
from taolib.task_queue.queue.redis_queue import RedisTaskQueue

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakePipeline:
    """模拟 Redis pipeline，支持 async with 上下文管理器。"""

    def __init__(self):
        self._calls = []
        self._execute_results = None

    def hset(self, name, mapping=None, **kwargs):
        self._calls.append(("hset", name, mapping))

    def lpush(self, name, *values):
        self._calls.append(("lpush", name, values))

    def hincrby(self, name, key, amount=1):
        self._calls.append(("hincrby", name, key, amount))

    def srem(self, name, *values):
        self._calls.append(("srem", name, values))

    def sadd(self, name, *values):
        self._calls.append(("sadd", name, values))

    def ltrim(self, name, start, end):
        self._calls.append(("ltrim", name, start, end))

    def delete(self, *names):
        self._calls.append(("delete", names))

    def zadd(self, name, mapping):
        self._calls.append(("zadd", name, mapping))

    def hgetall(self, name):
        self._calls.append(("hgetall", name))

    def llen(self, name):
        self._calls.append(("llen", name))

    def scard(self, name):
        self._calls.append(("scard", name))

    def zcard(self, name):
        self._calls.append(("zcard", name))

    async def execute(self):
        if self._execute_results is not None:
            return self._execute_results
        return [None] * len(self._calls)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


def _make_redis_and_pipeline():
    """创建 mock Redis 和 FakePipeline，使用 MagicMock 避免协程问题。"""
    redis = AsyncMock()
    pipe = FakePipeline()
    # 关键：pipeline() 是同步调用返回 async context manager，
    # 用 MagicMock 确保返回值不是协程
    redis.pipeline = MagicMock(return_value=pipe)
    return redis, pipe


def _make_queue(redis=None, prefix="tq"):
    if redis is None:
        redis, _ = _make_redis_and_pipeline()
    return RedisTaskQueue(redis=redis, key_prefix=prefix), redis


# ===========================================================================
# Key Generation Tests
# ===========================================================================


class TestKeyGeneration:
    """Redis 键生成测试。"""

    def test_key_with_default_prefix(self):
        queue, _ = _make_queue()
        assert queue._key("queue:high") == "tq:queue:high"

    def test_key_with_custom_prefix(self):
        queue, _ = _make_queue(prefix="myapp")
        assert queue._key("stats") == "myapp:stats"

    def test_queue_keys_order(self):
        queue, _ = _make_queue()
        keys = queue._queue_keys
        assert len(keys) == 3
        assert "high" in keys[0]
        assert "normal" in keys[1]
        assert "low" in keys[2]


# ===========================================================================
# Enqueue Tests
# ===========================================================================


class TestEnqueue:
    """入队操作测试。"""

    @pytest.mark.asyncio
    async def test_enqueue_normal_priority(self):
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        meta = {"task_type": "send_email", "priority": "normal", "status": "pending"}

        await queue.enqueue("task-001", TaskPriority.NORMAL, meta)

        ops = [c[0] for c in pipe._calls]
        assert "hset" in ops
        assert "lpush" in ops
        assert "hincrby" in ops

    @pytest.mark.asyncio
    async def test_enqueue_high_priority(self):
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.enqueue("task-002", TaskPriority.HIGH, {"task_type": "urgent"})

        lpush_calls = [c for c in pipe._calls if c[0] == "lpush"]
        assert len(lpush_calls) == 1
        assert "high" in lpush_calls[0][1]

    @pytest.mark.asyncio
    async def test_enqueue_low_priority(self):
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.enqueue("task-003", TaskPriority.LOW, {"task_type": "cleanup"})

        lpush_calls = [c for c in pipe._calls if c[0] == "lpush"]
        assert "low" in lpush_calls[0][1]


# ===========================================================================
# Dequeue Tests
# ===========================================================================


class TestDequeue:
    """出队操作测试。"""

    @pytest.mark.asyncio
    async def test_dequeue_returns_task_id(self):
        redis, _ = _make_redis_and_pipeline()
        redis.brpop.return_value = (b"tq:queue:high", b"task-001")

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.dequeue(timeout=5)

        assert result == "task-001"
        redis.sadd.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_dequeue_timeout_returns_none(self):
        redis, _ = _make_redis_and_pipeline()
        redis.brpop.return_value = None

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.dequeue(timeout=1)

        assert result is None

    @pytest.mark.asyncio
    async def test_dequeue_string_task_id(self):
        redis, _ = _make_redis_and_pipeline()
        redis.brpop.return_value = ("tq:queue:normal", "task-string")

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.dequeue()

        assert result == "task-string"


# ===========================================================================
# Ack Tests
# ===========================================================================


class TestAck:
    """任务确认测试。"""

    @pytest.mark.asyncio
    async def test_ack_removes_from_running(self):
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.ack("task-001")

        ops = [c[0] for c in pipe._calls]
        assert "srem" in ops
        assert "lpush" in ops
        assert "ltrim" in ops
        assert "hincrby" in ops
        assert "delete" in ops


# ===========================================================================
# Nack Tests
# ===========================================================================


class TestNack:
    """任务失败标记测试。"""

    @pytest.mark.asyncio
    async def test_nack_with_retry(self):
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        import time

        retry_at = time.time() + 60

        await queue.nack("task-001", schedule_retry=True, retry_at=retry_at)

        ops = [c[0] for c in pipe._calls]
        assert "srem" in ops
        assert "zadd" in ops
        assert "hincrby" in ops

    @pytest.mark.asyncio
    async def test_nack_without_retry(self):
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.nack("task-001", schedule_retry=False)

        ops = [c[0] for c in pipe._calls]
        assert "srem" in ops
        assert "sadd" in ops
        assert "zadd" not in ops


# ===========================================================================
# Poll Retries Tests
# ===========================================================================


class TestPollRetries:
    """重试轮询测试。"""

    @pytest.mark.asyncio
    async def test_poll_retries_empty(self):
        redis, _ = _make_redis_and_pipeline()
        redis.zrangebyscore.return_value = []

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.poll_retries()

        assert result == []

    @pytest.mark.asyncio
    async def test_poll_retries_re_enqueues(self):
        redis, _ = _make_redis_and_pipeline()
        redis.zrangebyscore.return_value = [b"task-001", b"task-002"]
        redis.zrem.return_value = 1
        redis.hget.return_value = b"normal"

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.poll_retries()

        assert len(result) == 2
        assert redis.lpush.await_count == 2

    @pytest.mark.asyncio
    async def test_poll_retries_default_priority(self):
        redis, _ = _make_redis_and_pipeline()
        redis.zrangebyscore.return_value = [b"task-no-meta"]
        redis.zrem.return_value = 1
        redis.hget.return_value = None

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.poll_retries()

        assert len(result) == 1
        lpush_call = redis.lpush.call_args
        assert "normal" in lpush_call[0][0]

    @pytest.mark.asyncio
    async def test_poll_retries_skips_already_removed(self):
        redis, _ = _make_redis_and_pipeline()
        redis.zrangebyscore.return_value = [b"task-gone"]
        redis.zrem.return_value = 0

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.poll_retries()

        assert result == []
        redis.lpush.assert_not_awaited()


# ===========================================================================
# Task Meta Tests
# ===========================================================================


class TestTaskMeta:
    """任务元数据缓存测试。"""

    @pytest.mark.asyncio
    async def test_get_task_meta_found(self):
        redis, _ = _make_redis_and_pipeline()
        redis.hgetall.return_value = {
            b"task_type": b"send_email",
            b"priority": b"normal",
        }

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        meta = await queue.get_task_meta("task-001")

        assert meta == {"task_type": "send_email", "priority": "normal"}

    @pytest.mark.asyncio
    async def test_get_task_meta_not_found(self):
        redis, _ = _make_redis_and_pipeline()
        redis.hgetall.return_value = {}

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        meta = await queue.get_task_meta("nonexistent")

        assert meta is None

    @pytest.mark.asyncio
    async def test_set_task_meta(self):
        redis, _ = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.set_task_meta("task-001", {"task_type": "job", "priority": "high"})
        redis.hset.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_task_meta_string_keys(self):
        redis, _ = _make_redis_and_pipeline()
        redis.hgetall.return_value = {
            "task_type": "send_email",
            "priority": "normal",
        }

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        meta = await queue.get_task_meta("task-001")

        assert meta == {"task_type": "send_email", "priority": "normal"}


# ===========================================================================
# Stats Tests
# ===========================================================================


class TestQueueStats:
    """队列统计测试。"""

    @pytest.mark.asyncio
    async def test_get_stats(self):
        redis, pipe = _make_redis_and_pipeline()

        # 模拟 execute 返回：hgetall, 3 llen, scard, scard, llen, zcard
        pipe._execute_results = [
            {b"total_submitted": b"100", b"total_completed": b"80"},
            5,  # queue:high
            10,  # queue:normal
            2,  # queue:low
            3,  # running
            1,  # failed
            80,  # completed_recent
            2,  # retrying
        ]

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        stats = await queue.get_stats()

        assert stats["total_submitted"] == 100
        assert stats["total_completed"] == 80
        assert stats["queue_high"] == 5
        assert stats["queue_normal"] == 10
        assert stats["queue_low"] == 2

    @pytest.mark.asyncio
    async def test_get_stats_empty(self):
        redis, pipe = _make_redis_and_pipeline()
        pipe._execute_results = [{}, 0, 0, 0, 0, 0, 0, 0]

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        stats = await queue.get_stats()

        assert stats["total_submitted"] == 0
        assert stats["queue_high"] == 0

    @pytest.mark.asyncio
    async def test_get_queue_lengths(self):
        redis, pipe = _make_redis_and_pipeline()
        pipe._execute_results = [5, 10, 2]

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        lengths = await queue.get_queue_lengths()

        assert lengths == {"high": 5, "normal": 10, "low": 2}


# ===========================================================================
# Running/Failed Management Tests
# ===========================================================================


class TestRunningFailedManagement:
    """运行中/失败集合管理测试。"""

    @pytest.mark.asyncio
    async def test_get_running_task_ids(self):
        redis, _ = _make_redis_and_pipeline()
        redis.smembers.return_value = {b"task-1", b"task-2"}

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        ids = await queue.get_running_task_ids()

        assert ids == {"task-1", "task-2"}

    @pytest.mark.asyncio
    async def test_get_running_task_ids_empty(self):
        redis, _ = _make_redis_and_pipeline()
        redis.smembers.return_value = set()

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        ids = await queue.get_running_task_ids()

        assert ids == set()

    @pytest.mark.asyncio
    async def test_remove_from_running(self):
        redis, _ = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.remove_from_running("task-001")
        redis.srem.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_remove_from_failed(self):
        redis, _ = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.remove_from_failed("task-001")
        redis.srem.assert_awaited_once()


# ===========================================================================
# Edge Case Tests
# ===========================================================================


class TestQueueEdgeCases:
    """队列边缘场景测试。"""

    @pytest.mark.asyncio
    async def test_get_running_task_ids_string_members(self):
        """smembers 返回 str（非 bytes）时正常处理。"""
        redis, _ = _make_redis_and_pipeline()
        redis.smembers.return_value = {"task-str-1", "task-str-2"}

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        ids = await queue.get_running_task_ids()

        assert ids == {"task-str-1", "task-str-2"}

    @pytest.mark.asyncio
    async def test_nack_retry_without_retry_at(self):
        """nack schedule_retry=True 但 retry_at=None → 走 failed 分支。"""
        redis, pipe = _make_redis_and_pipeline()
        queue = RedisTaskQueue(redis=redis, key_prefix="tq")

        await queue.nack("task-001", schedule_retry=True, retry_at=None)

        ops = [c[0] for c in pipe._calls]
        # 应走 failed 分支（else 分支），加入 failed set
        assert "sadd" in ops
        assert "zadd" not in ops

    @pytest.mark.asyncio
    async def test_poll_retries_string_ids(self):
        """zrangebyscore 返回 str（非 bytes）任务 ID。"""
        redis, _ = _make_redis_and_pipeline()
        redis.zrangebyscore.return_value = ["task-str-1"]
        redis.zrem.return_value = 1
        redis.hget.return_value = "high"

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.poll_retries()

        assert result == ["task-str-1"]
        redis.lpush.assert_awaited_once()
        # 验证入队到 high 队列
        lpush_args = redis.lpush.call_args[0]
        assert "high" in lpush_args[0]

    @pytest.mark.asyncio
    async def test_get_stats_string_keys(self):
        """hgetall 返回 str 键（非 bytes）时统计正常。"""
        redis, pipe = _make_redis_and_pipeline()
        pipe._execute_results = [
            {"total_submitted": "50", "total_completed": "30", "total_failed": "5"},
            3,
            7,
            1,
            2,
            1,
            30,
            0,
        ]

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        stats = await queue.get_stats()

        assert stats["total_submitted"] == 50
        assert stats["total_completed"] == 30
        assert stats["total_failed"] == 5

    @pytest.mark.asyncio
    async def test_dequeue_adds_to_running_set(self):
        """dequeue 成功后应将任务加入 running 集合。"""
        redis, _ = _make_redis_and_pipeline()
        redis.brpop.return_value = (b"tq:queue:normal", b"task-100")

        queue = RedisTaskQueue(redis=redis, key_prefix="tq")
        result = await queue.dequeue(timeout=5)

        assert result == "task-100"
        redis.sadd.assert_awaited_once_with("tq:running", "task-100")
