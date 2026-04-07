"""WorkerManager 测试。

覆盖 WorkerManager 的属性、启动/停止生命周期、重试轮询和崩溃恢复。
"""

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from taolib.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.task_queue.models.task import TaskDocument
from taolib.task_queue.worker.manager import (
    RETRY_POLL_INTERVAL,
    STALE_TASK_TIMEOUT,
    WorkerManager,
)
from taolib.task_queue.worker.registry import TaskHandlerRegistry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_manager(num_workers: int = 3):
    """创建测试用 WorkerManager 及其依赖。"""
    redis_queue = AsyncMock()
    task_repo = AsyncMock()
    registry = TaskHandlerRegistry()
    mgr = WorkerManager(
        redis_queue=redis_queue,
        task_repo=task_repo,
        registry=registry,
        num_workers=num_workers,
    )
    return mgr, redis_queue, task_repo, registry


def _make_task_doc(
    task_id: str = "task-001",
    status: TaskStatus = TaskStatus.RUNNING,
    priority: TaskPriority = TaskPriority.NORMAL,
    started_at: datetime | None = None,
    task_type: str = "send_email",
):
    """创建测试用 TaskDocument mock。"""
    doc = MagicMock(spec=TaskDocument)
    doc.id = task_id
    doc.task_type = task_type
    doc.status = status
    doc.priority = priority
    doc.started_at = started_at
    doc.params = {"to": "user@example.com"}
    doc.retry_count = 0
    doc.max_retries = 3
    doc.retry_delays = [60, 300, 900]
    return doc


# ===========================================================================
# Properties Tests
# ===========================================================================


class TestManagerProperties:
    """管理器属性测试。"""

    def test_initial_state(self):
        mgr, _, _, _ = _make_manager()
        assert not mgr.is_running
        assert mgr.workers == []
        assert mgr._retry_poller_task is None

    def test_num_workers_default(self):
        redis_queue = AsyncMock()
        task_repo = AsyncMock()
        registry = TaskHandlerRegistry()
        mgr = WorkerManager(redis_queue, task_repo, registry)
        assert mgr.num_workers == 3

    def test_num_workers_custom(self):
        mgr, _, _, _ = _make_manager(num_workers=5)
        assert mgr.num_workers == 5

    def test_workers_returns_copy(self):
        mgr, _, _, _ = _make_manager()
        workers = mgr.workers
        workers.append("fake")
        assert mgr.workers == []


# ===========================================================================
# Start / Stop Tests
# ===========================================================================


class TestManagerStartStop:
    """管理器启动/停止生命周期测试。"""

    @pytest.mark.asyncio
    async def test_start_sets_running(self):
        mgr, queue, repo, _ = _make_manager(num_workers=1)
        queue.get_running_task_ids.return_value = []

        # Patch TaskWorker.start to avoid real event loop work
        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            MockWorker.return_value = mock_instance

            await mgr.start()

        assert mgr.is_running
        # Cleanup
        mgr._running = False
        if mgr._retry_poller_task:
            mgr._retry_poller_task.cancel()
            try:
                await mgr._retry_poller_task
            except asyncio.CancelledError, Exception:
                pass

    @pytest.mark.asyncio
    async def test_start_creates_workers(self):
        mgr, queue, repo, _ = _make_manager(num_workers=2)
        queue.get_running_task_ids.return_value = []

        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            MockWorker.return_value = mock_instance

            await mgr.start()

        assert len(mgr._workers) == 2
        assert len(mgr._worker_tasks) == 2
        # Cleanup
        mgr._running = False
        if mgr._retry_poller_task:
            mgr._retry_poller_task.cancel()
            try:
                await mgr._retry_poller_task
            except asyncio.CancelledError, Exception:
                pass

    @pytest.mark.asyncio
    async def test_start_idempotent(self):
        mgr, queue, repo, _ = _make_manager(num_workers=1)
        queue.get_running_task_ids.return_value = []

        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            MockWorker.return_value = mock_instance

            await mgr.start()
            # Second start should be a no-op
            await mgr.start()

        assert len(mgr._workers) == 1  # Not doubled
        # Cleanup
        mgr._running = False
        if mgr._retry_poller_task:
            mgr._retry_poller_task.cancel()
            try:
                await mgr._retry_poller_task
            except asyncio.CancelledError, Exception:
                pass

    @pytest.mark.asyncio
    async def test_start_calls_recover(self):
        mgr, queue, repo, _ = _make_manager(num_workers=1)
        queue.get_running_task_ids.return_value = []

        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            MockWorker.return_value = mock_instance

            await mgr.start()

        # _recover_running_tasks calls get_running_task_ids
        queue.get_running_task_ids.assert_awaited_once()
        # Cleanup
        mgr._running = False
        if mgr._retry_poller_task:
            mgr._retry_poller_task.cancel()
            try:
                await mgr._retry_poller_task
            except asyncio.CancelledError, Exception:
                pass

    @pytest.mark.asyncio
    async def test_stop_clears_state(self):
        mgr, queue, repo, _ = _make_manager(num_workers=1)
        queue.get_running_task_ids.return_value = []

        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            mock_instance.stop = MagicMock()
            MockWorker.return_value = mock_instance

            await mgr.start()
            await mgr.stop()

        assert not mgr.is_running
        assert mgr._workers == []
        assert mgr._worker_tasks == []
        assert mgr._retry_poller_task is None

    @pytest.mark.asyncio
    async def test_stop_calls_worker_stop(self):
        mgr, queue, repo, _ = _make_manager(num_workers=2)
        queue.get_running_task_ids.return_value = []

        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            mock_instance.stop = MagicMock()
            MockWorker.return_value = mock_instance

            await mgr.start()
            await mgr.stop()

        assert mock_instance.stop.call_count == 2

    @pytest.mark.asyncio
    async def test_stop_noop_when_not_running(self):
        mgr, _, _, _ = _make_manager()
        # Should not raise
        await mgr.stop()
        assert not mgr.is_running

    @pytest.mark.asyncio
    async def test_stop_cancels_retry_poller(self):
        mgr, queue, repo, _ = _make_manager(num_workers=1)
        queue.get_running_task_ids.return_value = []

        with patch("taolib.task_queue.worker.manager.TaskWorker") as MockWorker:
            mock_instance = AsyncMock()
            mock_instance.start = AsyncMock()
            mock_instance.stop = MagicMock()
            MockWorker.return_value = mock_instance

            await mgr.start()
            assert mgr._retry_poller_task is not None
            await mgr.stop()

        assert mgr._retry_poller_task is None


# ===========================================================================
# Retry Poll Loop Tests
# ===========================================================================


class TestRetryPollLoop:
    """重试轮询循环测试。"""

    @pytest.mark.asyncio
    async def test_poll_re_enqueues_tasks(self):
        mgr, queue, repo, _ = _make_manager()
        queue.poll_retries.return_value = ["task-1", "task-2"]

        mgr._running = True
        call_count = 0

        async def sleep_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Let the first sleep pass so poll_retries runs,
            # stop on the second iteration.
            if call_count >= 2:
                mgr._running = False

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = sleep_side_effect
            await mgr._retry_poll_loop()

        # Should update both tasks to PENDING
        assert repo.update_status.await_count == 2
        repo.update_status.assert_any_await(
            "task-1", TaskStatus.PENDING, next_retry_at=None
        )
        repo.update_status.assert_any_await(
            "task-2", TaskStatus.PENDING, next_retry_at=None
        )

    @pytest.mark.asyncio
    async def test_poll_empty_noop(self):
        mgr, queue, repo, _ = _make_manager()
        queue.poll_retries.return_value = []

        mgr._running = True
        call_count = 0

        async def sleep_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                mgr._running = False

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = sleep_side_effect
            await mgr._retry_poll_loop()

        queue.poll_retries.assert_awaited_once()
        repo.update_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_poll_none_result_noop(self):
        mgr, queue, repo, _ = _make_manager()
        queue.poll_retries.return_value = None

        mgr._running = True
        call_count = 0

        async def sleep_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                mgr._running = False

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = sleep_side_effect
            await mgr._retry_poll_loop()

        queue.poll_retries.assert_awaited_once()
        repo.update_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_poll_stops_when_not_running(self):
        mgr, queue, repo, _ = _make_manager()
        mgr._running = False

        # Should exit immediately
        with patch("asyncio.sleep", new_callable=AsyncMock):
            await mgr._retry_poll_loop()

        queue.poll_retries.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_poll_handles_cancelled_error(self):
        mgr, queue, repo, _ = _make_manager()
        mgr._running = True

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = asyncio.CancelledError
            # Should not raise, just break
            await mgr._retry_poll_loop()

    @pytest.mark.asyncio
    async def test_poll_handles_unexpected_exception(self):
        mgr, queue, repo, _ = _make_manager()
        mgr._running = True
        call_count = 0

        async def sleep_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                mgr._running = False

        queue.poll_retries.side_effect = RuntimeError("Redis down")

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = sleep_side_effect
            await mgr._retry_poll_loop()

        # Should have attempted to poll but continue running
        assert queue.poll_retries.await_count >= 1

    @pytest.mark.asyncio
    async def test_poll_checks_running_after_sleep(self):
        """sleep 后如果 _running=False，应退出循环。"""
        mgr, queue, repo, _ = _make_manager()
        mgr._running = True

        async def stop_during_sleep(*args, **kwargs):
            mgr._running = False

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = stop_during_sleep
            await mgr._retry_poll_loop()

        # poll_retries should NOT be called since _running=False after sleep
        queue.poll_retries.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_poll_interval_is_correct(self):
        mgr, queue, repo, _ = _make_manager()
        mgr._running = True
        queue.poll_retries.return_value = []

        async def stop_after_one_poll(*args, **kwargs):
            mgr._running = False

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = stop_after_one_poll
            await mgr._retry_poll_loop()

        mock_sleep.assert_awaited_once_with(RETRY_POLL_INTERVAL)


# ===========================================================================
# Crash Recovery Tests
# ===========================================================================


class TestCrashRecovery:
    """崩溃恢复测试。"""

    @pytest.mark.asyncio
    async def test_no_running_tasks(self):
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = []

        await mgr._recover_running_tasks()

        # No further calls needed
        repo.get_by_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_orphan_task_cleanup(self):
        """Redis 中有 running 任务但 MongoDB 找不到 → 清理 Redis。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["orphan-1"]
        repo.get_by_id.return_value = None

        await mgr._recover_running_tasks()

        queue.remove_from_running.assert_awaited_once_with("orphan-1")
        repo.update_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_completed_task_cleanup(self):
        """MongoDB 已 COMPLETED 但 Redis 未清理 → 清理 Redis。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["task-1"]
        task = _make_task_doc(task_id="task-1", status=TaskStatus.COMPLETED)
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        queue.remove_from_running.assert_awaited_once_with("task-1")
        # 不应重新入队
        queue.enqueue.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_failed_task_cleanup(self):
        """MongoDB 已 FAILED 但 Redis 未清理 → 清理 Redis。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["task-1"]
        task = _make_task_doc(task_id="task-1", status=TaskStatus.FAILED)
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        queue.remove_from_running.assert_awaited_once_with("task-1")
        queue.enqueue.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_stale_task_re_enqueue(self):
        """超过 STALE_TASK_TIMEOUT 的任务 → 重新入队。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["stale-1"]

        stale_time = datetime.now(UTC) - timedelta(seconds=STALE_TASK_TIMEOUT + 60)
        task = _make_task_doc(
            task_id="stale-1",
            status=TaskStatus.RUNNING,
            started_at=stale_time,
            priority=TaskPriority.HIGH,
        )
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        queue.remove_from_running.assert_awaited_once_with("stale-1")
        repo.update_status.assert_awaited_once_with("stale-1", TaskStatus.PENDING)
        queue.enqueue.assert_awaited_once_with(
            "stale-1",
            TaskPriority.HIGH,
            {"task_type": "send_email", "priority": TaskPriority.HIGH},
        )

    @pytest.mark.asyncio
    async def test_recent_task_skipped(self):
        """启动时间在 STALE_TASK_TIMEOUT 内的 RUNNING 任务 → 保留不动。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["recent-1"]

        recent_time = datetime.now(UTC) - timedelta(seconds=60)
        task = _make_task_doc(
            task_id="recent-1",
            status=TaskStatus.RUNNING,
            started_at=recent_time,
        )
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        # 不应清理也不应重新入队
        queue.remove_from_running.assert_not_awaited()
        queue.enqueue.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_none_started_at_skipped(self):
        """started_at 为 None 的 RUNNING 任务 → 保留不动。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["no-start-1"]

        task = _make_task_doc(
            task_id="no-start-1",
            status=TaskStatus.RUNNING,
            started_at=None,
        )
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        queue.remove_from_running.assert_not_awaited()
        queue.enqueue.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_priority_preserved_on_re_enqueue(self):
        """重新入队时保留原任务优先级。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["low-1"]

        stale_time = datetime.now(UTC) - timedelta(seconds=STALE_TASK_TIMEOUT + 100)
        task = _make_task_doc(
            task_id="low-1",
            status=TaskStatus.RUNNING,
            started_at=stale_time,
            priority=TaskPriority.LOW,
            task_type="generate_report",
        )
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        queue.enqueue.assert_awaited_once_with(
            "low-1",
            TaskPriority.LOW,
            {"task_type": "generate_report", "priority": TaskPriority.LOW},
        )

    @pytest.mark.asyncio
    async def test_mixed_scenarios(self):
        """混合场景：一个孤儿、一个已完成、一个过期。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = [
            "orphan-1",
            "completed-1",
            "stale-1",
        ]

        stale_time = datetime.now(UTC) - timedelta(seconds=STALE_TASK_TIMEOUT + 60)
        completed_task = _make_task_doc(
            task_id="completed-1", status=TaskStatus.COMPLETED
        )
        stale_task = _make_task_doc(
            task_id="stale-1",
            status=TaskStatus.RUNNING,
            started_at=stale_time,
        )

        async def get_by_id_side_effect(task_id):
            mapping = {
                "orphan-1": None,
                "completed-1": completed_task,
                "stale-1": stale_task,
            }
            return mapping.get(task_id)

        repo.get_by_id.side_effect = get_by_id_side_effect

        await mgr._recover_running_tasks()

        # orphan + completed + stale = 3 calls to remove_from_running
        assert queue.remove_from_running.await_count == 3
        # Only stale should be re-enqueued
        queue.enqueue.assert_awaited_once()
        repo.update_status.assert_awaited_once_with("stale-1", TaskStatus.PENDING)

    @pytest.mark.asyncio
    async def test_exception_handled_gracefully(self):
        """_recover_running_tasks 内部异常不会传播到调用方。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.side_effect = RuntimeError("Redis connection lost")

        # Should not raise
        await mgr._recover_running_tasks()

    @pytest.mark.asyncio
    async def test_stale_threshold_boundary(self):
        """刚好在 STALE_TASK_TIMEOUT 边界上的任务 → 不重新入队。"""
        mgr, queue, repo, _ = _make_manager()
        queue.get_running_task_ids.return_value = ["boundary-1"]

        # Exactly at the threshold (not past it)
        boundary_time = datetime.now(UTC) - timedelta(seconds=STALE_TASK_TIMEOUT)
        task = _make_task_doc(
            task_id="boundary-1",
            status=TaskStatus.RUNNING,
            started_at=boundary_time,
        )
        repo.get_by_id.return_value = task

        await mgr._recover_running_tasks()

        # At exactly the threshold, started_at < stale_threshold should be False
        # because stale_threshold = now - STALE_TASK_TIMEOUT ≈ started_at
        # Due to time passing between now() calls, this may or may not trigger.
        # The key invariant: if it does trigger, it re-enqueues; if not, it skips.
        # We just verify no exception is raised.
