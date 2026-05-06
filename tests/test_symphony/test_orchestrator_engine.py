"""编排引擎核心逻辑测试。"""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from taolib.symphony.config.schema import (
    AgentConfig,
    CodexConfig,
    PollingConfig,
    SymphonyConfig,
    TrackerConfig,
    WorkerConfig,
)
from taolib.symphony.orchestrator.engine import Orchestrator
from taolib.symphony.orchestrator.state import (
    RetryEntry,
    RunningEntry,
)
from taolib.symphony.tracker.models import Issue


def _make_config(**overrides: object) -> SymphonyConfig:
    """构造测试用 SymphonyConfig。"""
    defaults = {
        "tracker": TrackerConfig(
            kind="linear",
            api_key="test-key",
            project_slug="test-proj",
            active_states=["Todo", "In Progress"],
            terminal_states=["Done", "Cancelled"],
        ),
        "polling": PollingConfig(interval_ms=5000),
        "agent": AgentConfig(max_concurrent_agents=5),
        "codex": CodexConfig(command="codex app-server"),
        "worker": WorkerConfig(),
    }
    defaults.update(overrides)
    return SymphonyConfig(**defaults)


def _make_issue(
    id: str = "issue-1",
    identifier: str = "ABC-123",
    title: str = "Test Issue",
    state: str = "Todo",
) -> Issue:
    """构造测试用 Issue。"""
    return Issue(
        id=id,
        identifier=identifier,
        title=title,
        state=state,
    )


def _make_orchestrator(**config_overrides: object) -> Orchestrator:
    """构造测试用 Orchestrator（依赖均 mock）。"""
    config = _make_config(**config_overrides)
    tracker = AsyncMock()
    workspace_manager = MagicMock()
    agent_runner = AsyncMock()
    return Orchestrator(config, tracker, workspace_manager, agent_runner)


class TestSelectWorkerHost:
    """测试 _select_worker_host 最小负载选择。"""

    def test_no_ssh_hosts_returns_none(self) -> None:
        """无 SSH 主机配置时返回 None（本地执行）。"""
        orch = _make_orchestrator()
        assert orch._select_worker_host() is None

    def test_selects_least_loaded_host(self) -> None:
        """选择当前运行 worker 数最少的主机。"""
        orch = _make_orchestrator(
            worker=WorkerConfig(ssh_hosts=["host1", "host2", "host3"]),
        )
        # host1 有 2 个 worker，host2 有 0 个，host3 有 1 个
        orch.state.running["issue-1"] = RunningEntry(
            identifier="A", worker_host="host1",
        )
        orch.state.running["issue-2"] = RunningEntry(
            identifier="B", worker_host="host1",
        )
        orch.state.running["issue-3"] = RunningEntry(
            identifier="C", worker_host="host3",
        )

        result = orch._select_worker_host()
        assert result == "host2"

    def test_selects_first_host_on_tie(self) -> None:
        """负载相同时选择列表中靠前的主机。"""
        orch = _make_orchestrator(
            worker=WorkerConfig(ssh_hosts=["host1", "host2"]),
        )
        # 两个主机均无 worker
        result = orch._select_worker_host()
        assert result == "host1"

    def test_ignores_unknown_hosts_in_running(self) -> None:
        """运行中 worker 的主机不在配置列表中时不影响选择。"""
        orch = _make_orchestrator(
            worker=WorkerConfig(ssh_hosts=["host1", "host2"]),
        )
        orch.state.running["issue-1"] = RunningEntry(
            identifier="A", worker_host="unknown-host",
        )

        result = orch._select_worker_host()
        # host1 和 host2 负载均为 0，选择第一个
        assert result in ("host1", "host2")


class TestRevalidateIssueForDispatch:
    """测试 _revalidate_issue_for_dispatch 防竞态调度。"""

    def test_valid_issue_passes(self) -> None:
        """正常 Issue 通过验证。"""
        orch = _make_orchestrator()
        issue = _make_issue()
        assert orch._revalidate_issue_for_dispatch(issue) is True

    def test_already_running_fails(self) -> None:
        """已在 running 中的 Issue 验证失败。"""
        orch = _make_orchestrator()
        issue = _make_issue()
        orch.state.running["issue-1"] = RunningEntry(identifier="ABC-123")
        assert orch._revalidate_issue_for_dispatch(issue) is False

    def test_already_claimed_fails(self) -> None:
        """已在 claimed 中的 Issue 验证失败。"""
        orch = _make_orchestrator()
        issue = _make_issue()
        orch.state.claimed.add("issue-1")
        assert orch._revalidate_issue_for_dispatch(issue) is False

    def test_in_retry_attempts_fails(self) -> None:
        """已在 retry_attempts 中的 Issue 验证失败。"""
        orch = _make_orchestrator()
        issue = _make_issue()
        orch.state.retry_attempts["issue-1"] = RetryEntry(identifier="ABC-123")
        assert orch._revalidate_issue_for_dispatch(issue) is False

    def test_missing_required_fields_fails(self) -> None:
        """缺少必要字段的 Issue 验证失败。"""
        orch = _make_orchestrator()
        # id 为空
        issue = _make_issue(id="", identifier="ABC-123")
        assert orch._revalidate_issue_for_dispatch(issue) is False

        # identifier 为空
        issue = _make_issue(id="issue-1", identifier="")
        assert orch._revalidate_issue_for_dispatch(issue) is False


class TestRefreshRuntimeConfig:
    """测试 _refresh_runtime_config 配置热重载。"""

    def test_syncs_poll_interval(self) -> None:
        """从配置同步轮询间隔。"""
        orch = _make_orchestrator(polling=PollingConfig(interval_ms=10000))
        orch.state.poll_interval_ms = 5000
        orch._refresh_runtime_config()
        assert orch.state.poll_interval_ms == 10000

    def test_syncs_max_concurrent_agents(self) -> None:
        """从配置同步最大并发数。"""
        orch = _make_orchestrator(agent=AgentConfig(max_concurrent_agents=3))
        orch.state.max_concurrent_agents = 10
        orch._refresh_runtime_config()
        assert orch.state.max_concurrent_agents == 3


class TestSnapshot:
    """测试 snapshot() 可观测性快照。"""

    def test_snapshot_returns_dict(self) -> None:
        """snapshot 返回包含核心字段的字典。"""
        orch = _make_orchestrator()
        result = orch.snapshot()

        assert isinstance(result, dict)
        assert "running" in result
        assert "retrying" in result
        assert "completed_count" in result
        assert "codex_totals" in result
        assert "poll_check_in_progress" in result
        assert "next_poll_due_at_ms" in result

    def test_snapshot_includes_poll_state(self) -> None:
        """快照包含轮询状态信息。"""
        orch = _make_orchestrator()
        orch.state.poll_check_in_progress = True
        orch.state.next_poll_due_at_ms = 12345.0

        result = orch.snapshot()
        assert result["poll_check_in_progress"] is True
        assert result["next_poll_due_at_ms"] == 12345.0

    def test_snapshot_includes_running_entry_with_host(self) -> None:
        """快照包含运行中 worker 的主机信息。"""
        orch = _make_orchestrator()
        orch.state.running["issue-1"] = RunningEntry(
            identifier="ABC-123",
            worker_host="host1",
            workspace_path="/tmp/ws",
        )

        result = orch.snapshot()
        assert len(result["running"]) == 1
        entry = result["running"][0]
        assert entry["worker_host"] == "host1"
        assert entry["workspace_path"] == "/tmp/ws"


class TestRetryTokenValidation:
    """测试 retry_token 防过期重试。"""

    @pytest.mark.asyncio
    async def test_valid_token_proceeds(self) -> None:
        """有效 token 的重试计时器正常执行。"""
        orch = _make_orchestrator()
        token = uuid.uuid4()

        # 设置重试条目
        orch.state.retry_attempts["issue-1"] = RetryEntry(
            issue_id="issue-1",
            identifier="ABC-123",
            attempt=1,
            retry_token=token,
        )
        orch.state.claimed.add("issue-1")

        # tracker 返回空候选（问题已不存在）
        orch._tracker.fetch_candidate_issues = AsyncMock(return_value=[])

        await orch._on_retry_timer("issue-1", token)

        # 问题未找到，应释放声明
        assert "issue-1" not in orch.state.claimed

    @pytest.mark.asyncio
    async def test_mismatch_token_skips_and_restores(self) -> None:
        """token 不匹配时跳过执行，保留更新的重试条目。"""
        orch = _make_orchestrator()
        old_token = uuid.uuid4()
        new_token = uuid.uuid4()

        # 当前条目的 token 是新的
        current_entry = RetryEntry(
            issue_id="issue-1",
            identifier="ABC-123",
            attempt=2,
            retry_token=new_token,
        )
        orch.state.retry_attempts["issue-1"] = current_entry

        # 用旧 token 触发回调
        await orch._on_retry_timer("issue-1", old_token)

        # 新的重试条目应被保留
        assert "issue-1" in orch.state.retry_attempts
        assert orch.state.retry_attempts["issue-1"].retry_token == new_token
        assert orch.state.retry_attempts["issue-1"].attempt == 2


class TestDelayType:
    """测试 delay_type 区分续运/故障。"""

    @pytest.mark.asyncio
    async def test_continuation_delay_type(self) -> None:
        """正常退出产生 continuation 类型的重试。"""
        orch = _make_orchestrator()

        # 构造正常完成的 worker
        async def _noop() -> None:
            pass

        task = asyncio.create_task(_noop(), name="worker:ABC-123")
        entry = RunningEntry(
            worker_task=task,
            identifier="ABC-123",
            worker_host="host1",
            workspace_path="/tmp/ws",
        )
        orch.state.running["issue-1"] = entry
        orch.state.claimed.add("issue-1")

        # 等待 task 完成
        await task

        # 触发回调
        orch._on_worker_done("issue-1", task)

        # 检查重试条目
        assert "issue-1" in orch.state.retry_attempts
        retry = orch.state.retry_attempts["issue-1"]
        assert retry.delay_type == "continuation"
        assert retry.worker_host == "host1"
        assert retry.workspace_path == "/tmp/ws"

        # 清理计时器
        retry.timer_handle.cancel()

    @pytest.mark.asyncio
    async def test_failure_delay_type(self) -> None:
        """异常退出产生 failure 类型的重试。"""
        orch = _make_orchestrator()

        # 构造异常完成的 worker
        async def _fail() -> None:
            raise RuntimeError("test error")

        task = asyncio.create_task(_fail(), name="worker:DEF-456")
        entry = RunningEntry(
            worker_task=task,
            identifier="DEF-456",
            worker_host="host2",
            workspace_path="/tmp/ws2",
            retry_attempt=1,
        )
        orch.state.running["issue-2"] = entry
        orch.state.claimed.add("issue-2")

        # 等待 task 异常完成
        try:
            await task
        except RuntimeError:
            pass

        # 触发回调
        orch._on_worker_done("issue-2", task)

        # 检查重试条目
        assert "issue-2" in orch.state.retry_attempts
        retry = orch.state.retry_attempts["issue-2"]
        assert retry.delay_type == "failure"
        assert retry.worker_host == "host2"
        assert retry.error is not None

        # 清理计时器
        retry.timer_handle.cancel()


class TestPollCheckInProgress:
    """测试 poll_check_in_progress 生命周期。"""

    @pytest.mark.asyncio
    async def test_tick_sets_and_clears_poll_flag(self) -> None:
        """_tick 执行期间设置 poll_check_in_progress，结束后清除。"""
        orch = _make_orchestrator()

        # tracker 返回空候选
        orch._tracker.fetch_candidate_issues = AsyncMock(return_value=[])

        # 在 tick 前检查
        assert orch.state.poll_check_in_progress is False

        await orch._tick()

        # tick 后应已清除
        assert orch.state.poll_check_in_progress is False

    @pytest.mark.asyncio
    async def test_tick_sets_next_poll_due_at(self) -> None:
        """_tick 结束后设置 next_poll_due_at_ms。"""
        orch = _make_orchestrator(polling=PollingConfig(interval_ms=5000))

        orch._tracker.fetch_candidate_issues = AsyncMock(return_value=[])

        assert orch.state.next_poll_due_at_ms is None

        await orch._tick()

        assert orch.state.next_poll_due_at_ms is not None
        # 应大约等于当前时间 + interval_ms
        import time
        now_ms = time.monotonic() * 1000
        expected = now_ms + 5000
        # 允许 2 秒误差
        assert abs(orch.state.next_poll_due_at_ms - expected) < 2000
