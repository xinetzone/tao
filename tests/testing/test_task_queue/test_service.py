"""任务服务测试。

覆盖 TaskService 的提交、查询、重试、取消和统计操作。
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.task_queue.errors import TaskAlreadyExistsError, TaskNotFoundError
from taolib.testing.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.testing.task_queue.models.task import TaskCreate, TaskDocument
from taolib.testing.task_queue.services.task_service import TaskService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task_doc(
    task_id="task-001",
    task_type="send_email",
    status=TaskStatus.PENDING,
    priority=TaskPriority.NORMAL,
    retry_count=0,
    idempotency_key=None,
    error_message=None,
):
    doc = MagicMock(spec=TaskDocument)
    doc.id = task_id
    doc.task_type = task_type
    doc.status = status
    doc.priority = priority
    doc.retry_count = retry_count
    doc.idempotency_key = idempotency_key
    doc.error_message = error_message
    doc.params = {"to": "user@example.com"}
    doc.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    doc.to_response.return_value = MagicMock(id=task_id, status=status)
    return doc


def _make_service():
    task_repo = AsyncMock()
    redis_queue = AsyncMock()
    svc = TaskService(task_repo=task_repo, redis_queue=redis_queue)
    return svc, task_repo, redis_queue


# ===========================================================================
# Submit Task Tests
# ===========================================================================


class TestSubmitTask:
    """任务提交测试。"""

    @pytest.mark.asyncio
    async def test_submit_success(self):
        svc, repo, queue = _make_service()
        repo.find_by_idempotency_key.return_value = None
        task_doc = _make_task_doc()
        repo.create.return_value = task_doc

        task_create = TaskCreate(
            task_type="send_email",
            params={"to": "user@example.com"},
        )

        result = await svc.submit_task(task_create)

        assert result is task_doc
        repo.create.assert_awaited_once()
        queue.enqueue.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_submit_with_priority(self):
        svc, repo, queue = _make_service()
        repo.find_by_idempotency_key.return_value = None
        repo.create.return_value = _make_task_doc(priority=TaskPriority.HIGH)

        task_create = TaskCreate(
            task_type="critical_job",
            params={},
            priority=TaskPriority.HIGH,
        )

        await svc.submit_task(task_create)

        enqueue_call = queue.enqueue.call_args
        assert enqueue_call[0][1] == TaskPriority.HIGH

    @pytest.mark.asyncio
    async def test_submit_with_idempotency_key_unique(self):
        svc, repo, queue = _make_service()
        repo.find_by_idempotency_key.return_value = None
        repo.create.return_value = _make_task_doc()

        task_create = TaskCreate(
            task_type="send_email",
            params={},
            idempotency_key="unique-key-123",
        )

        result = await svc.submit_task(task_create)
        repo.find_by_idempotency_key.assert_awaited_once_with("unique-key-123")
        assert result is not None

    @pytest.mark.asyncio
    async def test_submit_with_idempotency_key_duplicate(self):
        svc, repo, _ = _make_service()
        repo.find_by_idempotency_key.return_value = _make_task_doc()

        task_create = TaskCreate(
            task_type="send_email",
            params={},
            idempotency_key="duplicate-key",
        )

        with pytest.raises(TaskAlreadyExistsError, match="already exists"):
            await svc.submit_task(task_create)

    @pytest.mark.asyncio
    async def test_submit_without_idempotency_key(self):
        svc, repo, queue = _make_service()
        repo.create.return_value = _make_task_doc()

        task_create = TaskCreate(
            task_type="send_email",
            params={},
        )

        result = await svc.submit_task(task_create)
        repo.find_by_idempotency_key.assert_not_awaited()
        assert result is not None

    @pytest.mark.asyncio
    async def test_submit_stores_correct_status(self):
        svc, repo, _ = _make_service()
        repo.create.return_value = _make_task_doc()

        task_create = TaskCreate(task_type="job", params={})
        await svc.submit_task(task_create)

        create_call = repo.create.call_args[0][0]
        assert create_call["status"] == TaskStatus.PENDING
        assert create_call["retry_count"] == 0

    @pytest.mark.asyncio
    async def test_submit_enqueues_with_meta(self):
        svc, repo, queue = _make_service()
        repo.create.return_value = _make_task_doc()

        task_create = TaskCreate(
            task_type="process_data",
            params={"file": "data.csv"},
            priority=TaskPriority.LOW,
        )

        await svc.submit_task(task_create)

        enqueue_call = queue.enqueue.call_args
        meta = enqueue_call[0][2]
        assert meta["task_type"] == "process_data"
        assert meta["priority"] == TaskPriority.LOW
        assert meta["status"] == TaskStatus.PENDING


# ===========================================================================
# Get Task Tests
# ===========================================================================


class TestGetTask:
    """任务查询测试。"""

    @pytest.mark.asyncio
    async def test_get_existing_task(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc()

        result = await svc.get_task("task-001")
        assert result.id == "task-001"

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundError, match="not found"):
            await svc.get_task("nonexistent")


# ===========================================================================
# Retry Task Tests
# ===========================================================================


class TestRetryTask:
    """任务重试测试。"""

    @pytest.mark.asyncio
    async def test_retry_failed_task(self):
        svc, repo, queue = _make_service()
        failed_task = _make_task_doc(status=TaskStatus.FAILED, retry_count=3)
        repo.get_by_id.return_value = failed_task
        updated_task = _make_task_doc(status=TaskStatus.PENDING, retry_count=0)
        repo.update_status.return_value = updated_task

        result = await svc.retry_task("task-001")

        repo.update_status.assert_awaited_once()
        queue.remove_from_failed.assert_awaited_once_with("task-001")
        queue.enqueue.assert_awaited_once()
        # 验证 retry_count 重置为 0
        call_kwargs = repo.update_status.call_args
        assert call_kwargs[1]["retry_count"] == 0

    @pytest.mark.asyncio
    async def test_retry_non_failed_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.RUNNING)

        with pytest.raises(ValueError, match="Only failed tasks"):
            await svc.retry_task("task-001")

    @pytest.mark.asyncio
    async def test_retry_pending_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.PENDING)

        with pytest.raises(ValueError, match="Only failed tasks"):
            await svc.retry_task("task-001")

    @pytest.mark.asyncio
    async def test_retry_completed_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.COMPLETED)

        with pytest.raises(ValueError, match="Only failed tasks"):
            await svc.retry_task("task-001")

    @pytest.mark.asyncio
    async def test_retry_nonexistent_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            await svc.retry_task("nonexistent")


# ===========================================================================
# Cancel Task Tests
# ===========================================================================


class TestCancelTask:
    """任务取消测试。"""

    @pytest.mark.asyncio
    async def test_cancel_pending_task(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.PENDING)
        repo.update_status.return_value = _make_task_doc(status=TaskStatus.CANCELLED)

        result = await svc.cancel_task("task-001")
        repo.update_status.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancel_retrying_task(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.RETRYING)
        repo.update_status.return_value = _make_task_doc(status=TaskStatus.CANCELLED)

        result = await svc.cancel_task("task-001")
        repo.update_status.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_cancel_running_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.RUNNING)

        with pytest.raises(ValueError, match="Only pending or retrying"):
            await svc.cancel_task("task-001")

    @pytest.mark.asyncio
    async def test_cancel_completed_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.COMPLETED)

        with pytest.raises(ValueError, match="Only pending or retrying"):
            await svc.cancel_task("task-001")

    @pytest.mark.asyncio
    async def test_cancel_failed_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = _make_task_doc(status=TaskStatus.FAILED)

        with pytest.raises(ValueError, match="Only pending or retrying"):
            await svc.cancel_task("task-001")

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task_raises(self):
        svc, repo, _ = _make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(TaskNotFoundError):
            await svc.cancel_task("nonexistent")


# ===========================================================================
# List Tasks Tests
# ===========================================================================


class TestListTasks:
    """任务列表查询测试。"""

    @pytest.mark.asyncio
    async def test_list_all(self):
        svc, repo, _ = _make_service()
        repo.find_by_filters.return_value = [_make_task_doc(), _make_task_doc()]

        result = await svc.list_tasks()
        assert len(result) == 2
        repo.find_by_filters.assert_awaited_once_with(
            status=None, task_type=None, priority=None, skip=0, limit=100
        )

    @pytest.mark.asyncio
    async def test_list_by_status(self):
        svc, repo, _ = _make_service()
        repo.find_by_filters.return_value = [_make_task_doc(status=TaskStatus.FAILED)]

        result = await svc.list_tasks(status=TaskStatus.FAILED)
        repo.find_by_filters.assert_awaited_once_with(
            status=TaskStatus.FAILED, task_type=None, priority=None, skip=0, limit=100
        )

    @pytest.mark.asyncio
    async def test_list_by_type(self):
        svc, repo, _ = _make_service()
        repo.find_by_filters.return_value = []

        await svc.list_tasks(task_type="send_email")
        repo.find_by_filters.assert_awaited_once_with(
            status=None, task_type="send_email", priority=None, skip=0, limit=100
        )

    @pytest.mark.asyncio
    async def test_list_with_pagination(self):
        svc, repo, _ = _make_service()
        repo.find_by_filters.return_value = []

        await svc.list_tasks(skip=20, limit=10)
        repo.find_by_filters.assert_awaited_once_with(
            status=None, task_type=None, priority=None, skip=20, limit=10
        )


# ===========================================================================
# Stats Tests
# ===========================================================================


class TestGetStats:
    """统计信息测试。"""

    @pytest.mark.asyncio
    async def test_get_stats_merges_data(self):
        svc, repo, queue = _make_service()

        queue.get_stats.return_value = {
            "queue_high": 5,
            "queue_normal": 10,
            "queue_low": 2,
            "total_submitted": 100,
            "total_completed": 80,
            "total_failed": 10,
            "total_retried": 5,
        }

        repo.count.side_effect = [20, 3, 70, 8, 2, 103]

        result = await svc.get_stats()

        assert result["pending"] == 20
        assert result["running"] == 3
        assert result["completed"] == 70
        assert result["failed"] == 8
        assert result["retrying"] == 2
        assert result["total_tasks"] == 103
        assert result["queue_high"] == 5
        assert result["queue_normal"] == 10
        assert result["queue_low"] == 2
        assert result["total_submitted"] == 100



