"""任务工作协程测试。

覆盖 TaskWorker 的任务处理、成功/失败处理和重试逻辑。
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from taolib.testing.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.testing.task_queue.models.task import TaskDocument
from taolib.testing.task_queue.worker.registry import TaskHandlerRegistry
from taolib.testing.task_queue.worker.worker import TaskWorker

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task_doc(
    task_id="task-001",
    task_type="send_email",
    status=TaskStatus.PENDING,
    retry_count=0,
    max_retries=3,
    retry_delays=None,
):
    """创建测试用 TaskDocument mock。"""
    doc = MagicMock(spec=TaskDocument)
    doc.id = task_id
    doc.task_type = task_type
    doc.status = status
    doc.retry_count = retry_count
    doc.max_retries = max_retries
    doc.retry_delays = retry_delays or [60, 300, 900]
    doc.params = {"to": "user@example.com"}
    doc.priority = TaskPriority.NORMAL
    doc.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    return doc


def _make_worker(registry=None):
    """创建测试用 TaskWorker 及其依赖。"""
    redis_queue = AsyncMock()
    task_repo = AsyncMock()
    if registry is None:
        registry = TaskHandlerRegistry()
    worker = TaskWorker(
        worker_id="test-worker-0",
        redis_queue=redis_queue,
        task_repo=task_repo,
        registry=registry,
    )
    return worker, redis_queue, task_repo


# ===========================================================================
# Worker Properties Tests
# ===========================================================================


class TestWorkerProperties:
    """Worker 属性测试。"""

    def test_worker_id(self):
        worker, _, _ = _make_worker()
        assert worker.worker_id == "test-worker-0"

    def test_initial_state(self):
        worker, _, _ = _make_worker()
        assert not worker.is_running
        assert worker.current_task_id is None


# ===========================================================================
# Process Task Tests - Success
# ===========================================================================


class TestProcessTaskSuccess:
    """任务成功处理测试。"""

    @pytest.mark.asyncio
    async def test_successful_async_handler(self):
        registry = TaskHandlerRegistry()

        @registry.handler("send_email")
        async def handle(params):
            return {"sent": True}

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc()
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        # 验证状态更新为 RUNNING，然后 COMPLETED
        assert repo.update_status.await_count == 2
        queue.ack.assert_awaited_once_with("task-001")

    @pytest.mark.asyncio
    async def test_successful_sync_handler(self):
        registry = TaskHandlerRegistry()

        @registry.handler("sync_task")
        def handle(params):
            return {"done": True}

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(task_type="sync_task")
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        queue.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handler_returns_none(self):
        registry = TaskHandlerRegistry()

        @registry.handler("void_task")
        async def handle(params):
            return None

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(task_type="void_task")
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        queue.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_handler_returns_non_dict(self):
        registry = TaskHandlerRegistry()

        @registry.handler("string_task")
        async def handle(params):
            return "hello"

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(task_type="string_task")
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        queue.ack.assert_awaited_once()


# ===========================================================================
# Process Task Tests - Failure & Retry
# ===========================================================================


class TestProcessTaskFailure:
    """任务失败与重试测试。"""

    @pytest.mark.asyncio
    async def test_handler_failure_with_retries_remaining(self):
        registry = TaskHandlerRegistry()

        @registry.handler("failing_task")
        async def handle(params):
            raise ValueError("Something went wrong")

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(
            task_type="failing_task",
            retry_count=0,
            max_retries=3,
        )
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        # 应该调度重试（nack with schedule_retry=True）
        queue.nack.assert_awaited_once()
        nack_kwargs = queue.nack.call_args[1]
        assert nack_kwargs["schedule_retry"] is True
        assert nack_kwargs["retry_at"] is not None

    @pytest.mark.asyncio
    async def test_handler_failure_max_retries_exceeded(self):
        registry = TaskHandlerRegistry()

        @registry.handler("final_fail")
        async def handle(params):
            raise RuntimeError("Fatal error")

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(
            task_type="final_fail",
            retry_count=2,
            max_retries=3,
        )
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        # 应该标记为最终失败（nack with schedule_retry=False）
        queue.nack.assert_awaited_once()
        nack_kwargs = queue.nack.call_args[1]
        assert nack_kwargs["schedule_retry"] is False

    @pytest.mark.asyncio
    async def test_failure_stores_error_info(self):
        registry = TaskHandlerRegistry()

        @registry.handler("error_info_task")
        async def handle(params):
            raise ValueError("detailed error message")

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(
            task_type="error_info_task",
            retry_count=0,
            max_retries=3,
        )
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        # 验证更新调用包含错误信息
        update_call = repo.update_status.call_args_list[-1]
        assert "error_message" in update_call[1]
        assert "error_traceback" in update_call[1]


# ===========================================================================
# Process Task Tests - Edge Cases
# ===========================================================================


class TestProcessTaskEdgeCases:
    """边缘情况测试。"""

    @pytest.mark.asyncio
    async def test_task_not_found_in_mongodb(self):
        worker, queue, repo = _make_worker()
        repo.get_by_id.return_value = None

        await worker._process_task("orphan-task")

        # 应该直接 ack（清理孤儿任务）
        queue.ack.assert_awaited_once_with("orphan-task")

    @pytest.mark.asyncio
    async def test_cancelled_task_skipped(self):
        worker, queue, repo = _make_worker()
        task_doc = _make_task_doc(status=TaskStatus.CANCELLED)
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        queue.ack.assert_awaited_once()
        # 不应该更新状态为 RUNNING
        repo.update_status.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_handler_registered(self):
        registry = TaskHandlerRegistry()
        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(task_type="unknown_type")
        repo.get_by_id.return_value = task_doc

        await worker._process_task("task-001")

        # 应该调用 nack（无处理器是致命错误）
        queue.nack.assert_awaited_once()


# ===========================================================================
# Stop / Graceful Shutdown Tests
# ===========================================================================


class TestWorkerLifecycle:
    """Worker 生命周期测试。"""

    def test_stop_sets_flag(self):
        worker, _, _ = _make_worker()
        worker._running = True
        worker.stop()
        assert not worker._running

    @pytest.mark.asyncio
    async def test_run_loop_exits_on_stop(self):
        worker, queue, _ = _make_worker()
        queue.dequeue.return_value = None

        # 启动后立即停止
        worker._running = True
        worker.stop()

        # _run_loop 应该在一次迭代后退出
        await worker._run_loop()

    @pytest.mark.asyncio
    async def test_current_task_id_tracked(self):
        registry = TaskHandlerRegistry()

        @registry.handler("tracking_task")
        async def handle(params):
            return {}

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc(task_type="tracking_task")
        repo.get_by_id.return_value = task_doc

        # 处理前应为 None
        assert worker.current_task_id is None

        await worker._process_task("task-001")

        # 处理后也应为 None（finally 清理）
        assert worker.current_task_id is None


# ===========================================================================
# _run_loop Tests
# ===========================================================================


class TestRunLoop:
    """_run_loop 主工作循环测试。"""

    @pytest.mark.asyncio
    async def test_run_loop_processes_task(self):
        """dequeue 返回任务 ID 时，调用 _process_task。"""
        registry = TaskHandlerRegistry()

        @registry.handler("send_email")
        async def handle(params):
            return {"ok": True}

        worker, queue, repo = _make_worker(registry)
        task_doc = _make_task_doc()
        repo.get_by_id.return_value = task_doc

        call_count = 0

        async def dequeue_side_effect(timeout=5.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "task-001"
            worker._running = False
            return None

        queue.dequeue.side_effect = dequeue_side_effect
        worker._running = True

        await worker._run_loop()

        # 验证 process_task 被调用（通过 repo.get_by_id 判断）
        repo.get_by_id.assert_awaited_once_with("task-001")
        queue.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_loop_skips_none_dequeue(self):
        """dequeue 返回 None 时，继续循环。"""
        worker, queue, repo = _make_worker()
        call_count = 0

        async def dequeue_side_effect(timeout=5.0):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                worker._running = False
            return None

        queue.dequeue.side_effect = dequeue_side_effect
        worker._running = True

        await worker._run_loop()

        # dequeue 被调用多次，但 repo.get_by_id 不应被调用
        assert queue.dequeue.await_count >= 2
        repo.get_by_id.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_run_loop_handles_cancelled_error(self):
        """CancelledError 导致循环退出。"""
        worker, queue, repo = _make_worker()
        queue.dequeue.side_effect = asyncio.CancelledError
        worker._running = True

        await worker._run_loop()

        # 应正常退出，无异常
        assert queue.dequeue.await_count == 1

    @pytest.mark.asyncio
    async def test_run_loop_handles_unexpected_error(self):
        """意外异常后 sleep(1) 然后继续。"""
        worker, queue, repo = _make_worker()
        call_count = 0

        async def dequeue_side_effect(timeout=5.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("unexpected")
            worker._running = False
            return None

        queue.dequeue.side_effect = dequeue_side_effect
        worker._running = True

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await worker._run_loop()

        mock_sleep.assert_awaited_once_with(1)

    @pytest.mark.asyncio
    async def test_run_loop_clears_current_task_id_on_error(self):
        """_process_task 异常时仍清理 current_task_id。"""
        worker, queue, repo = _make_worker()
        repo.get_by_id.side_effect = RuntimeError("db error")
        call_count = 0

        async def dequeue_side_effect(timeout=5.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "task-err"
            worker._running = False
            return None

        queue.dequeue.side_effect = dequeue_side_effect
        worker._running = True

        with patch("asyncio.sleep", new_callable=AsyncMock):
            await worker._run_loop()

        assert worker.current_task_id is None

    @pytest.mark.asyncio
    async def test_start_sets_running_and_cleans_up(self):
        """start() 设置 _running=True，退出后设为 False。"""
        worker, queue, repo = _make_worker()

        async def dequeue_side_effect(timeout=5.0):
            worker._running = False
            return None

        queue.dequeue.side_effect = dequeue_side_effect

        await worker.start()

        # start() 完成后 _running 应为 False
        assert not worker.is_running

    @pytest.mark.asyncio
    async def test_run_loop_multiple_tasks(self):
        """连续处理多个任务。"""
        registry = TaskHandlerRegistry()

        @registry.handler("send_email")
        async def handle(params):
            return {}

        worker, queue, repo = _make_worker(registry)
        task_doc1 = _make_task_doc(task_id="task-001")
        task_doc2 = _make_task_doc(task_id="task-002")
        call_count = 0

        async def dequeue_side_effect(timeout=5.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return "task-001"
            if call_count == 2:
                return "task-002"
            worker._running = False
            return None

        async def get_by_id_side_effect(task_id):
            return {"task-001": task_doc1, "task-002": task_doc2}.get(task_id)

        queue.dequeue.side_effect = dequeue_side_effect
        repo.get_by_id.side_effect = get_by_id_side_effect
        worker._running = True

        await worker._run_loop()

        assert repo.get_by_id.await_count == 2
        assert queue.ack.await_count == 2



