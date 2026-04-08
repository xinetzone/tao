"""TaskRepository 测试。

使用 MockMongoCollection 模拟 Motor 集合进行测试。
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.testing.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.testing.task_queue.repository.task_repo import TaskRepository

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class MockMongoCollection:
    """轻量级 Motor 集合模拟。"""

    def __init__(self):
        self.insert_one = AsyncMock()
        self.find_one = AsyncMock()
        self.find_one_and_update = AsyncMock()
        self.delete_one = AsyncMock()
        self.count_documents = AsyncMock(return_value=0)
        self.create_index = AsyncMock()
        self._find_results = []

    def find(self, *args, **kwargs):
        chain = MagicMock()
        chain.skip.return_value = chain
        chain.limit.return_value = chain
        chain.sort.return_value = chain
        chain.to_list = AsyncMock(return_value=self._find_results)
        return chain


# ===========================================================================
# Init & Create Index Tests
# ===========================================================================


class TestTaskRepositoryInit:
    """Repository 初始化测试。"""

    def test_init(self):
        repo = TaskRepository(MockMongoCollection())
        assert repo is not None

    @pytest.mark.asyncio
    async def test_create_indexes(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        await repo.create_indexes()
        assert col.create_index.call_count == 4


# ===========================================================================
# Find Methods Tests
# ===========================================================================


class TestFindMethods:
    """查询方法测试。"""

    @pytest.mark.asyncio
    async def test_find_by_status(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_by_status(TaskStatus.PENDING)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_by_type(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_by_type("send_email")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_failed_tasks(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_failed_tasks()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_running_tasks(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_running_tasks()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_by_idempotency_key_not_found(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_by_idempotency_key("nonexistent-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_filters_empty(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_by_filters()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_by_filters_with_all_params(self):
        col = MockMongoCollection()
        repo = TaskRepository(col)
        result = await repo.find_by_filters(
            status=TaskStatus.FAILED,
            task_type="send_email",
            priority=TaskPriority.HIGH,
            skip=10,
            limit=5,
        )
        assert isinstance(result, list)


# ===========================================================================
# Update Status Tests
# ===========================================================================


class TestUpdateStatus:
    """更新状态测试。"""

    @pytest.mark.asyncio
    async def test_update_status_success(self):
        col = MockMongoCollection()
        col.find_one_and_update.return_value = {
            "_id": "test-123",
            "task_type": "send_email",
            "params": {},
            "priority": "normal",
            "max_retries": 3,
            "retry_delays": [60, 300, 900],
            "status": "running",
            "retry_count": 0,
            "created_at": "2025-01-01T00:00:00+00:00",
            "tags": [],
        }
        repo = TaskRepository(col)
        result = await repo.update_status("test-123", TaskStatus.RUNNING)
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_status_not_found(self):
        col = MockMongoCollection()
        col.find_one_and_update.return_value = None
        repo = TaskRepository(col)
        result = await repo.update_status("nonexistent", TaskStatus.RUNNING)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_status_with_extra_fields(self):
        col = MockMongoCollection()
        col.find_one_and_update.return_value = {
            "_id": "test-123",
            "task_type": "send_email",
            "params": {},
            "priority": "normal",
            "max_retries": 3,
            "retry_delays": [60, 300, 900],
            "status": "completed",
            "retry_count": 0,
            "created_at": "2025-01-01T00:00:00+00:00",
            "tags": [],
            "result": {"sent": True},
        }
        repo = TaskRepository(col)
        result = await repo.update_status(
            "test-123",
            TaskStatus.COMPLETED,
            result={"sent": True},
        )
        assert result is not None



