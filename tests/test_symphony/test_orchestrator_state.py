"""编排器状态数据结构测试。"""

import uuid

from taolib.symphony.orchestrator.state import (
    OrchestratorState,
    RetryEntry,
    RetryMeta,
    RunningEntry,
)


class TestRunningEntry:
    """测试 RunningEntry 数据结构。"""

    def test_default_values(self) -> None:
        """默认值正确初始化。"""
        entry = RunningEntry()
        assert entry.worker_task is None
        assert entry.identifier == ""
        assert entry.issue_state == ""
        assert entry.worker_host is None
        assert entry.workspace_path is None
        assert entry.session_id is None
        assert entry.codex_input_tokens == 0
        assert entry.turn_count == 0
        assert entry.retry_attempt is None

    def test_new_fields_assignment(self) -> None:
        """新字段 worker_host/workspace_path 可正确赋值。"""
        entry = RunningEntry(
            identifier="ABC-123",
            worker_host="worker-1.example.com",
            workspace_path="/tmp/workspaces/ABC-123",
        )
        assert entry.worker_host == "worker-1.example.com"
        assert entry.workspace_path == "/tmp/workspaces/ABC-123"

    def test_new_fields_default_none(self) -> None:
        """新字段默认为 None（本地执行模式）。"""
        entry = RunningEntry(identifier="ABC-123")
        assert entry.worker_host is None
        assert entry.workspace_path is None


class TestRetryMeta:
    """测试 RetryMeta 数据结构。"""

    def test_default_values(self) -> None:
        """默认值正确初始化。"""
        meta = RetryMeta()
        assert meta.identifier == ""
        assert meta.delay_type == "failure"
        assert meta.error is None
        assert meta.worker_host is None
        assert meta.workspace_path is None

    def test_continuation_meta(self) -> None:
        """续运重试元数据构造正确。"""
        meta = RetryMeta(
            identifier="ABC-123",
            delay_type="continuation",
            error=None,
            worker_host="worker-1.example.com",
            workspace_path="/tmp/workspaces/ABC-123",
        )
        assert meta.delay_type == "continuation"
        assert meta.error is None
        assert meta.worker_host == "worker-1.example.com"

    def test_failure_meta(self) -> None:
        """故障重试元数据构造正确。"""
        meta = RetryMeta(
            identifier="DEF-456",
            delay_type="failure",
            error="worker exited: timeout",
        )
        assert meta.delay_type == "failure"
        assert meta.error == "worker exited: timeout"


class TestRetryEntry:
    """测试 RetryEntry 数据结构。"""

    def test_default_values(self) -> None:
        """默认值正确初始化。"""
        entry = RetryEntry()
        assert entry.issue_id == ""
        assert entry.identifier == ""
        assert entry.attempt == 1
        assert entry.delay_type == "failure"
        assert entry.error is None
        assert entry.worker_host is None
        assert entry.workspace_path is None

    def test_retry_token_auto_generated(self) -> None:
        """retry_token 自动生成且唯一。"""
        entry1 = RetryEntry(issue_id="id1", identifier="ABC-123")
        entry2 = RetryEntry(issue_id="id2", identifier="DEF-456")
        assert isinstance(entry1.retry_token, uuid.UUID)
        assert isinstance(entry2.retry_token, uuid.UUID)
        assert entry1.retry_token != entry2.retry_token

    def test_delay_type_continuation(self) -> None:
        """续运重试 delay_type 为 continuation。"""
        entry = RetryEntry(
            issue_id="id1",
            identifier="ABC-123",
            delay_type="continuation",
        )
        assert entry.delay_type == "continuation"

    def test_new_fields_from_meta(self) -> None:
        """从 RetryMeta 构造的 RetryEntry 字段一致。"""
        meta = RetryMeta(
            identifier="ABC-123",
            delay_type="failure",
            error="timeout",
            worker_host="host1",
            workspace_path="/tmp/ws",
        )
        entry = RetryEntry(
            issue_id="id1",
            identifier=meta.identifier,
            delay_type=meta.delay_type,
            error=meta.error,
            worker_host=meta.worker_host,
            workspace_path=meta.workspace_path,
        )
        assert entry.delay_type == "failure"
        assert entry.error == "timeout"
        assert entry.worker_host == "host1"
        assert entry.workspace_path == "/tmp/ws"


class TestOrchestratorState:
    """测试 OrchestratorState 数据结构。"""

    def test_default_values(self) -> None:
        """默认值正确初始化。"""
        state = OrchestratorState()
        assert state.poll_interval_ms == 30_000
        assert state.max_concurrent_agents == 10
        assert state.poll_check_in_progress is False
        assert state.next_poll_due_at_ms is None
        assert state.running == {}
        assert state.claimed == set()
        assert state.retry_attempts == {}
        assert state.completed == set()

    def test_poll_check_in_progress_toggle(self) -> None:
        """poll_check_in_progress 可正确切换。"""
        state = OrchestratorState()
        assert state.poll_check_in_progress is False

        state.poll_check_in_progress = True
        assert state.poll_check_in_progress is True

        state.poll_check_in_progress = False
        assert state.poll_check_in_progress is False

    def test_next_poll_due_at_ms(self) -> None:
        """next_poll_due_at_ms 可正确设置。"""
        state = OrchestratorState()
        assert state.next_poll_due_at_ms is None

        state.next_poll_due_at_ms = 12345.0
        assert state.next_poll_due_at_ms == 12345.0

    def test_running_entry_with_new_fields(self) -> None:
        """OrchestratorState.running 可存储含新字段的 RunningEntry。"""
        state = OrchestratorState()
        entry = RunningEntry(
            identifier="ABC-123",
            worker_host="worker-1",
            workspace_path="/tmp/ws/ABC-123",
        )
        state.running["issue-1"] = entry

        assert state.running["issue-1"].worker_host == "worker-1"
        assert state.running["issue-1"].workspace_path == "/tmp/ws/ABC-123"

    def test_retry_entry_with_new_fields(self) -> None:
        """OrchestratorState.retry_attempts 可存储含新字段的 RetryEntry。"""
        state = OrchestratorState()
        entry = RetryEntry(
            issue_id="issue-1",
            identifier="ABC-123",
            delay_type="continuation",
            worker_host="worker-1",
            workspace_path="/tmp/ws/ABC-123",
        )
        state.retry_attempts["issue-1"] = entry

        assert state.retry_attempts["issue-1"].delay_type == "continuation"
        assert state.retry_attempts["issue-1"].worker_host == "worker-1"
