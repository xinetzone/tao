"""共享测试夹具。"""

from datetime import UTC, datetime

import pytest

from taolib.testing.task_queue.models.enums import TaskPriority, TaskStatus
from taolib.testing.task_queue.models.task import TaskCreate, TaskDocument


@pytest.fixture
def sample_task_create() -> TaskCreate:
    """创建测试用的 TaskCreate 实例。"""
    return TaskCreate(
        task_type="send_email",
        params={"to": "user@example.com", "subject": "Hello"},
        priority=TaskPriority.NORMAL,
        max_retries=3,
        retry_delays=[60, 300, 900],
        tags=["email", "notification"],
    )


@pytest.fixture
def sample_task_document() -> TaskDocument:
    """创建测试用的 TaskDocument 实例。"""
    return TaskDocument(
        _id="abc123def456",
        task_type="send_email",
        params={"to": "user@example.com", "subject": "Hello"},
        priority=TaskPriority.NORMAL,
        max_retries=3,
        retry_delays=[60, 300, 900],
        status=TaskStatus.PENDING,
        retry_count=0,
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
        tags=["email"],
    )


@pytest.fixture
def sample_failed_task() -> TaskDocument:
    """创建测试用的失败 TaskDocument 实例。"""
    return TaskDocument(
        _id="failed123",
        task_type="generate_report",
        params={"report_id": "rpt-001"},
        priority=TaskPriority.HIGH,
        max_retries=3,
        retry_delays=[60, 300, 900],
        status=TaskStatus.FAILED,
        retry_count=3,
        error_message="Connection timeout",
        error_traceback="Traceback (most recent call last):\n  ...",
        created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
        started_at=datetime(2025, 1, 1, 12, 0, 1, tzinfo=UTC),
        completed_at=datetime(2025, 1, 1, 12, 0, 5, tzinfo=UTC),
    )



