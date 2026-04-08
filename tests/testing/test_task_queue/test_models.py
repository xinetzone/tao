"""模型和枚举测试。"""

from datetime import UTC, datetime

import pytest

from taolib.testing.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.testing.task_queue.models.task import (
    TaskCreate,
    TaskDocument,
    TaskResponse,
    TaskUpdate,
)


class TestTaskStatus:
    """TaskStatus 枚举测试。"""

    def test_values(self):
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.RETRYING == "retrying"
        assert TaskStatus.CANCELLED == "cancelled"

    def test_all_members(self):
        assert len(TaskStatus) == 6


class TestTaskPriority:
    """TaskPriority 枚举测试。"""

    def test_values(self):
        assert TaskPriority.HIGH == "high"
        assert TaskPriority.NORMAL == "normal"
        assert TaskPriority.LOW == "low"

    def test_all_members(self):
        assert len(TaskPriority) == 3


class TestTaskCreate:
    """TaskCreate 模型测试。"""

    def test_create_with_defaults(self):
        task = TaskCreate(task_type="send_email")
        assert task.task_type == "send_email"
        assert task.params == {}
        assert task.priority == TaskPriority.NORMAL
        assert task.max_retries == 3
        assert task.retry_delays == [60, 300, 900]
        assert task.idempotency_key is None
        assert task.tags == []

    def test_create_with_all_fields(self):
        task = TaskCreate(
            task_type="generate_report",
            params={"report_id": "rpt-001"},
            priority=TaskPriority.HIGH,
            max_retries=5,
            retry_delays=[30, 60, 120, 300, 600],
            idempotency_key="unique-key-123",
            tags=["report", "urgent"],
        )
        assert task.task_type == "generate_report"
        assert task.params == {"report_id": "rpt-001"}
        assert task.priority == TaskPriority.HIGH
        assert task.max_retries == 5
        assert task.retry_delays == [30, 60, 120, 300, 600]
        assert task.idempotency_key == "unique-key-123"
        assert task.tags == ["report", "urgent"]

    def test_create_validation_empty_type(self):
        with pytest.raises(Exception):
            TaskCreate(task_type="")

    def test_create_validation_max_retries(self):
        with pytest.raises(Exception):
            TaskCreate(task_type="test", max_retries=-1)


class TestTaskUpdate:
    """TaskUpdate 模型测试。"""

    def test_all_optional(self):
        update = TaskUpdate()
        data = update.model_dump(exclude_none=True)
        assert data == {}

    def test_partial_update(self):
        update = TaskUpdate(
            status=TaskStatus.RUNNING,
            started_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        data = update.model_dump(exclude_none=True)
        assert data["status"] == TaskStatus.RUNNING
        assert "started_at" in data
        assert "retry_count" not in data


class TestTaskDocument:
    """TaskDocument 模型测试。"""

    def test_create_with_defaults(self):
        doc = TaskDocument(
            _id="test-123",
            task_type="send_email",
        )
        assert doc.id == "test-123"
        assert doc.status == TaskStatus.PENDING
        assert doc.retry_count == 0
        assert doc.result is None
        assert doc.error_message is None
        assert doc.created_at is not None

    def test_to_response(self):
        now = datetime.now(UTC)
        doc = TaskDocument(
            _id="test-123",
            task_type="send_email",
            params={"to": "user@example.com"},
            priority=TaskPriority.HIGH,
            max_retries=3,
            retry_delays=[60, 300, 900],
            status=TaskStatus.COMPLETED,
            retry_count=1,
            result={"sent": True},
            created_at=now,
            started_at=now,
            completed_at=now,
            tags=["email"],
        )
        response = doc.to_response()
        assert isinstance(response, TaskResponse)
        assert response.id == "test-123"
        assert response.task_type == "send_email"
        assert response.priority == TaskPriority.HIGH
        assert response.status == TaskStatus.COMPLETED
        assert response.retry_count == 1
        assert response.result == {"sent": True}
        assert response.tags == ["email"]

    def test_to_response_with_error(self):
        doc = TaskDocument(
            _id="err-123",
            task_type="generate_report",
            status=TaskStatus.FAILED,
            retry_count=3,
            error_message="Timeout",
            error_traceback="Traceback...",
            created_at=datetime.now(UTC),
        )
        response = doc.to_response()
        assert response.status == TaskStatus.FAILED
        assert response.error_message == "Timeout"
        assert response.error_traceback == "Traceback..."



