"""Symphony 编排引擎 — 轮询、对账、分派与重试的完整生命周期。

Orchestrator 是 Symphony 服务的核心组件，拥有轮询节拍和内存中的运行时状态。
负责决定哪些问题需要分派、重试、停止或释放。

设计原则：
- 单线程 asyncio 事件循环，所有状态变更串行化
- asyncio.Task per worker，使用命名 task（Python 3.14 内省）
- 通过单一权威状态 (OrchestratorState) 避免重复分派
- 对账在每个节拍的分派之前运行
- 重启恢复由跟踪器驱动和文件系统驱动（无需持久化调度器数据库）

对应规范 §7（编排状态机）、§8（轮询、调度和对账）。
"""

import asyncio
import time
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

from taolib.symphony.config.schema import SymphonyConfig
from taolib.symphony.orchestrator.scheduler import Scheduler
from taolib.symphony.orchestrator.state import (
    OrchestratorState,
    RetryEntry,
    RetryMeta,
    RunningEntry,
)
from taolib.symphony.tracker.base import TrackerClient
from taolib.symphony.tracker.models import Issue
from taolib.symphony.workspace.manager import WorkspaceManager

logger = structlog.get_logger()


class DispatchValidationError(Exception):
    """分派预检验证失败。"""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons = reasons
        super().__init__("; ".join(reasons))


class Orchestrator:
    """Symphony 编排引擎。

    负责轮询 → 对账 → 分派 → 监控的完整生命周期。
    单线程 asyncio 事件循环，所有状态变更串行化。

    对应规范 §7（编排状态机）和 §8（轮询、调度和对账）。

    用法::

        config = SymphonyConfig()
        tracker = LinearTrackerClient(...)
        workspace_mgr = WorkspaceManager(...)
        agent_runner = AgentRunner(...)

        orch = Orchestrator(config, tracker, workspace_mgr, agent_runner)
        await orch.run()  # 阻塞直到 shutdown
    """

    def __init__(
        self,
        config: SymphonyConfig,
        tracker: TrackerClient,
        workspace_manager: WorkspaceManager,
        agent_runner: Any,  # AgentRunner — 使用 Any 避免循环导入
        *,
        scheduler: Scheduler | None = None,
    ) -> None:
        self._config = config
        self._tracker = tracker
        self._workspace_manager = workspace_manager
        self._agent_runner = agent_runner
        self._scheduler = scheduler or Scheduler()
        self._running = False

        # 从配置初始化编排器状态
        self.state = OrchestratorState(
            poll_interval_ms=config.polling.interval_ms,
            max_concurrent_agents=config.agent.max_concurrent_agents,
        )

    # ====================================================================
    # 公共接口
    # ====================================================================

    async def run(self) -> None:
        """服务主循环：启动验证 → 终态清理 → 首次 tick → 周期性 tick。

        阻塞调用，直到 shutdown() 被调用。

        对应规范 §16.1 服务启动：
        1. 配置验证
        2. 启动终态工作区清理
        3. 即时首次 tick
        4. 周期性 tick
        """
        self._running = True

        # 1. 启动验证
        try:
            self._validate_dispatch_config()
        except DispatchValidationError as exc:
            logger.error("startup_validation_failed", reasons=exc.reasons)
            raise

        logger.info(
            "orchestrator_starting",
            poll_interval_ms=self.state.poll_interval_ms,
            max_concurrent_agents=self.state.max_concurrent_agents,
        )

        # 2. 终态清理
        await self._startup_terminal_cleanup()

        # 3. 首次 tick（立即执行）
        await self._tick()

        # 4. 周期性 tick
        while self._running:
            await asyncio.sleep(self.state.poll_interval_ms / 1000)
            await self._tick()

    async def shutdown(self) -> None:
        """优雅关闭：停止新分派，等待活跃 worker，清理重试计时器。

        对应规范 §14 操作员干预 — 重启服务场景。
        """
        logger.info("orchestrator_shutdown_initiated")
        self._running = False

        # 取消所有重试计时器
        for _issue_id, retry_entry in list(self.state.retry_attempts.items()):
            retry_entry.timer_handle.cancel()
        self.state.retry_attempts.clear()

        # 等待活跃 worker（最多 30 秒）
        active_tasks = [
            entry.worker_task
            for entry in self.state.running.values()
            if entry.worker_task is not None and not entry.worker_task.done()
        ]

        if active_tasks:
            logger.info(
                "waiting_for_active_workers",
                count=len(active_tasks),
                timeout_s=30,
            )
            try:
                await asyncio.wait_for(
                    asyncio.gather(*active_tasks, return_exceptions=True),
                    timeout=30,
                )
            except TimeoutError:
                logger.warning("shutdown_timeout_cancelling_workers")
                for task in active_tasks:
                    if not task.done():
                        task.cancel()
                # 等待取消完成
                await asyncio.gather(*active_tasks, return_exceptions=True)

        # 运行时统计汇总
        logger.info(
            "orchestrator_shutdown_complete",
            completed=len(self.state.completed),
            codex_totals={
                "input_tokens": self.state.codex_totals.input_tokens,
                "output_tokens": self.state.codex_totals.output_tokens,
                "total_tokens": self.state.codex_totals.total_tokens,
                "seconds_running": self.state.codex_totals.seconds_running,
            },
        )

    # ====================================================================
    # Tick 节拍
    # ====================================================================

    async def _tick(self) -> None:
        """轮询和分派节拍。

        对应规范 §16.2 轮询和分派节拍：
        1. 对账运行中的问题（停顿检测 + 跟踪器状态刷新）
        2. 运行分派预检验证
        3. 使用活跃状态从跟踪器获取候选问题
        4. 按分派优先级排序问题
        5. 在槽位可用时分派符合条件的问题
        """
        # 设置轮询状态（供仪表板渲染）
        self.state.poll_check_in_progress = True
        try:
            # 1. 对账
            await self._reconcile_running_issues()

            # 2. 分派预检验证
            try:
                self._validate_dispatch_config()
            except DispatchValidationError as exc:
                logger.error("dispatch_validation_failed_tick", reasons=exc.reasons)
                return

            # 3. 获取候选问题
            try:
                candidates = await self._tracker.fetch_candidate_issues()
            except Exception:
                logger.exception("fetch_candidates_failed")
                return

            if not candidates:
                logger.debug("no_candidates")
                return

            # 4 & 5. 排序并分派
            dispatchable = self._scheduler.filter_dispatchable(
                candidates, self.state, self._config.agent
            )

            for issue in dispatchable:
                self._dispatch_issue(issue, attempt=None)

            if dispatchable:
                logger.info(
                    "dispatched_issues",
                    count=len(dispatchable),
                    identifiers=[i.identifier for i in dispatchable],
                )
        finally:
            self.state.poll_check_in_progress = False
            # 设置下次轮询到期时间
            self.state.next_poll_due_at_ms = (
                time.monotonic() * 1000 + self.state.poll_interval_ms
            )

    # ====================================================================
    # 分派
    # ====================================================================

    def _dispatch_issue(self, issue: Issue, attempt: int | None) -> None:
        """分派一个 issue，创建命名 worker task。

        对应规范 §16.4 分派一个问题。

        Args:
            issue: 待分派的问题
            attempt: 重试尝试序号（首次为 None）
        """
        # 幂等性检查：已在 running/claimed/retry 中的跳过
        if issue.id in self.state.running:
            logger.warning(
                "dispatch_skip_already_running",
                issue_id=issue.id,
                issue_identifier=issue.identifier,
            )
            return
        if issue.id in self.state.claimed:
            logger.warning(
                "dispatch_skip_already_claimed",
                issue_id=issue.id,
                issue_identifier=issue.identifier,
            )
            return
        if issue.id in self.state.retry_attempts:
            # 取消现有重试计时器
            existing = self.state.retry_attempts.pop(issue.id)
            existing.timer_handle.cancel()

        # 防竞态调度：分派前重新验证 Issue 有效性
        if not self._revalidate_issue_for_dispatch(issue):
            logger.warning(
                "dispatch_skip_revalidation_failed",
                issue_id=issue.id,
                issue_identifier=issue.identifier,
            )
            return

        # 选择 worker 主机（SSH 扩展：最小负载选择）
        worker_host = self._select_worker_host()

        # 创建命名 worker task（Python 3.14 内省支持）
        task = asyncio.create_task(
            self._run_worker(issue, attempt),
            name=f"worker:{issue.identifier}",
        )
        task.add_done_callback(lambda t: self._on_worker_done(issue.id, t))

        # 更新状态
        now = datetime.now(UTC)
        self.state.running[issue.id] = RunningEntry(
            worker_task=task,
            identifier=issue.identifier,
            issue_state=issue.state,
            worker_host=worker_host,
            retry_attempt=attempt if attempt is not None else None,
            started_at=now,
        )
        self.state.claimed.add(issue.id)

        # 移除可能存在的重试条目
        if issue.id in self.state.retry_attempts:
            retry = self.state.retry_attempts.pop(issue.id)
            retry.timer_handle.cancel()

        logger.info(
            "dispatched",
            issue_id=issue.id,
            issue_identifier=issue.identifier,
            attempt=attempt,
            task_name=task.get_name(),
            worker_host=worker_host,
        )

    # ====================================================================
    # Worker 执行
    # ====================================================================

    async def _run_worker(self, issue: Issue, attempt: int | None) -> None:
        """Worker 协程：运行智能体尝试。

        对应规范 §16.5 Worker 尝试（工作区 + 提示词 + 智能体）。

        Args:
            issue: 待处理的问题
            attempt: 重试尝试序号
        """
        issue_id = issue.id
        identifier = issue.identifier

        log = logger.bind(issue_id=issue_id, issue_identifier=identifier)

        try:
            await self._agent_runner.run_agent_attempt(
                issue=issue,
                attempt=attempt,
                on_update=self._make_update_callback(issue_id),
            )
        except asyncio.CancelledError:
            log.info("worker_cancelled")
            raise
        except Exception as exc:
            log.error("worker_failed", error=str(exc))
            raise

    def _make_update_callback(self, issue_id: str):
        """创建 Codex 事件更新回调。

        回调在编排器事件循环线程中同步执行，
        因此可以安全修改 state。

        Args:
            issue_id: 问题 ID

        Returns:
            回调函数
        """
        def on_update(event: str, identifier: str, payload: dict[str, Any]) -> None:
            entry = self.state.running.get(issue_id)
            if entry is None:
                return

            entry.last_codex_event = event
            entry.last_codex_timestamp = datetime.now(UTC)

            # 提取消息摘要
            if "message" in payload:
                msg = payload["message"]
                entry.last_codex_message = msg[:200] if isinstance(msg, str) else str(msg)[:200]

            # 提取会话 ID
            if "session_id" in payload:
                entry.session_id = payload["session_id"]
            if "codex_app_server_pid" in payload:
                entry.codex_app_server_pid = payload["codex_app_server_pid"]

            # 令牌计数更新（使用绝对总计，规范 §13.5）
            usage = payload.get("usage") or payload.get("total_token_usage")
            if usage and isinstance(usage, dict):
                inp = usage.get("input_tokens", 0)
                out = usage.get("output_tokens", 0)
                tot = usage.get("total_tokens", 0)

                if isinstance(inp, int) and isinstance(out, int) and isinstance(tot, int):
                    # 使用绝对总计：计算增量避免重复计数
                    delta_inp = max(inp - entry.last_reported_input_tokens, 0)
                    delta_out = max(out - entry.last_reported_output_tokens, 0)
                    delta_tot = max(tot - entry.last_reported_total_tokens, 0)

                    entry.codex_input_tokens = inp
                    entry.codex_output_tokens = out
                    entry.codex_total_tokens = tot
                    entry.last_reported_input_tokens = inp
                    entry.last_reported_output_tokens = out
                    entry.last_reported_total_tokens = tot

                    # 累积到全局总计
                    self.state.codex_totals.input_tokens += delta_inp
                    self.state.codex_totals.output_tokens += delta_out
                    self.state.codex_totals.total_tokens += delta_tot

            # 轮次计数
            if event in ("turn_completed", "turn_failed", "turn_cancelled"):
                entry.turn_count += 1

            # 速率限制跟踪
            rate_limits = payload.get("rate_limits")
            if rate_limits and isinstance(rate_limits, dict):
                self.state.codex_rate_limits = rate_limits

        return on_update

    # ====================================================================
    # Worker 完成回调
    # ====================================================================

    def _on_worker_done(self, issue_id: str, task: asyncio.Task) -> None:
        """Worker 完成回调：续运重试或故障指数退避重试。

        对应规范 §7.3 转换触发器 — Worker Exit：
        - 正常退出：安排续运重试（delay_type="continuation"，1 秒延迟）
        - 异常退出：安排指数退避重试（delay_type="failure"）

        此回调在事件循环线程中执行，可安全修改 state。

        Args:
            issue_id: 问题 ID
            task: 完成的 worker task
        """
        entry = self.state.running.pop(issue_id, None)
        if entry is None:
            return

        # 更新运行时统计
        elapsed = (datetime.now(UTC) - entry.started_at).total_seconds()
        self.state.codex_totals.seconds_running += elapsed

        identifier = entry.identifier
        log = logger.bind(issue_id=issue_id, issue_identifier=identifier)

        if task.cancelled():
            log.info("worker_cancelled_removing_claim")
            self.state.claimed.discard(issue_id)
            return

        exc = task.exception()
        if exc is None:
            # 正常退出：续运重试（规范 §7.3 Worker Exit normal）
            self.state.completed.add(issue_id)
            log.info("worker_normal_exit_scheduling_continuation")
            self._schedule_retry(
                issue_id=issue_id,
                attempt=1,
                meta=RetryMeta(
                    identifier=identifier,
                    delay_type="continuation",
                    error=None,
                    worker_host=entry.worker_host,
                    workspace_path=entry.workspace_path,
                ),
            )
        else:
            # 异常退出：指数退避重试（规范 §7.3 Worker Exit abnormal）
            next_attempt = (entry.retry_attempt or 0) + 1
            error_msg = f"worker exited: {exc}"
            log.warning(
                "worker_abnormal_exit_scheduling_retry",
                attempt=next_attempt,
                error=error_msg,
            )
            self._schedule_retry(
                issue_id=issue_id,
                attempt=next_attempt,
                meta=RetryMeta(
                    identifier=identifier,
                    delay_type="failure",
                    error=error_msg,
                    worker_host=entry.worker_host,
                    workspace_path=entry.workspace_path,
                ),
            )

    # ====================================================================
    # 重试调度
    # ====================================================================

    def _schedule_retry(
        self,
        issue_id: str,
        attempt: int,
        meta: RetryMeta,
    ) -> None:
        """安排一次重试。

        对应规范 §8.4 重试和退避。

        退避公式：
        - 续运重试（delay_type="continuation"）：固定 1000 ms 延迟
        - 故障重试（delay_type="failure"）：delay = min(10000 * 2^(attempt-1), max_retry_backoff_ms)

        retry_token 用于防止过期重试（参考 Elixir make_ref() 模式）：
        当同一 Issue 被重新调度时，旧计时器的 token 将不匹配，
        避免过期回调触发重复分派。

        Args:
            issue_id: 问题 ID
            attempt: 重试尝试序号
            meta: 重试调度元数据
        """
        # 取消同一问题的现有重试计时器
        existing = self.state.retry_attempts.get(issue_id)
        if existing is not None:
            existing.timer_handle.cancel()

        is_continuation = meta.delay_type == "continuation"
        delay_ms = self._compute_retry_delay_ms(attempt, is_continuation)
        due_at_ms = time.monotonic() * 1000 + delay_ms

        # 生成唯一 retry_token
        token = uuid.uuid4()

        # 使用事件循环的 call_later 安排重试触发
        loop = asyncio.get_running_loop()
        timer_handle = loop.call_later(
            delay_ms / 1000,
            lambda: asyncio.create_task(
                self._on_retry_timer(issue_id, token),
                name=f"retry:{meta.identifier}:{attempt}",
            ),
        )

        self.state.retry_attempts[issue_id] = RetryEntry(
            issue_id=issue_id,
            identifier=meta.identifier,
            attempt=attempt,
            due_at_ms=due_at_ms,
            timer_handle=timer_handle,
            retry_token=token,
            delay_type=meta.delay_type,
            error=meta.error,
            worker_host=meta.worker_host,
            workspace_path=meta.workspace_path,
        )

        logger.debug(
            "retry_scheduled",
            issue_id=issue_id,
            issue_identifier=meta.identifier,
            attempt=attempt,
            delay_ms=delay_ms,
            delay_type=meta.delay_type,
            retry_token=str(token)[:8],
        )

    def _compute_retry_delay_ms(self, attempt: int, is_continuation: bool) -> int:
        """计算重试延迟。

        对应规范 §8.4 退避公式：
        - 续运重试：1000 ms 固定延迟
        - 故障重试：delay = min(10000 * 2^(attempt-1), max_retry_backoff_ms)

        Args:
            attempt: 重试尝试序号（从 1 开始）
            is_continuation: 是否为续运重试

        Returns:
            延迟毫秒数
        """
        if is_continuation:
            return 1000
        return min(
            10_000 * (2 ** (attempt - 1)),
            self._config.agent.max_retry_backoff_ms,
        )

    async def _on_retry_timer(self, issue_id: str, retry_token: uuid.UUID) -> None:
        """重试计时器触发回调。

        对应规范 §16.6 on_retry_timer：
        1. 验证 retry_token（防过期重试）
        2. 获取活跃候选问题
        3. 按 issue_id 查找特定问题
        4. 如果未找到，释放声明
        5. 如果找到且仍符合候选条件，分派
        6. 如果找到但不再活跃，释放声明
        7. 如果槽位不可用，以错误重新排队

        Args:
            issue_id: 触发重试的问题 ID
            retry_token: 重试令牌，不匹配则跳过（防止过期重试）
        """
        retry_entry = self.state.retry_attempts.pop(issue_id, None)
        if retry_entry is None:
            return

        # retry_token 验证：不匹配则跳过（过期或已被新重试替换）
        if retry_entry.retry_token != retry_token:
            logger.debug(
                "retry_token_mismatch_skipping",
                issue_id=issue_id,
                expected=str(retry_token)[:8],
                actual=str(retry_entry.retry_token)[:8],
            )
            # 放回重试条目（token 不匹配意味着有更新的重试已调度）
            self.state.retry_attempts[issue_id] = retry_entry
            return

        identifier = retry_entry.identifier
        attempt = retry_entry.attempt
        log = logger.bind(issue_id=issue_id, issue_identifier=identifier, attempt=attempt)

        # 获取活跃候选
        try:
            candidates = await self._tracker.fetch_candidate_issues()
        except Exception:
            log.exception("retry_poll_failed")
            self._schedule_retry(
                issue_id=issue_id,
                attempt=attempt + 1,
                meta=RetryMeta(
                    identifier=identifier,
                    delay_type="failure",
                    error="retry poll failed",
                    worker_host=retry_entry.worker_host,
                    workspace_path=retry_entry.workspace_path,
                ),
            )
            return

        # 按 ID 查找
        issue = next((c for c in candidates if c.id == issue_id), None)

        if issue is None:
            # 问题不再出现在候选中，释放声明
            log.info("retry_issue_not_found_releasing_claim")
            self.state.claimed.discard(issue_id)
            return

        # 检查问题是否仍活跃
        terminal_lower = {s.lower() for s in self._config.tracker.terminal_states}
        active_lower = {s.lower() for s in self._config.tracker.active_states}

        if issue.state.lower() in terminal_lower:
            log.info("retry_issue_terminal_releasing_claim")
            self.state.claimed.discard(issue_id)
            return

        if issue.state.lower() not in active_lower:
            log.info("retry_issue_not_active_releasing_claim", issue_state=issue.state)
            self.state.claimed.discard(issue_id)
            return

        # 检查槽位
        global_slots = self._scheduler.available_slots(self.state)
        if global_slots <= 0:
            log.warning("retry_no_slots_requeuing")
            self._schedule_retry(
                issue_id=issue_id,
                attempt=attempt + 1,
                meta=RetryMeta(
                    identifier=identifier,
                    delay_type="failure",
                    error="no available orchestrator slots",
                    worker_host=retry_entry.worker_host,
                    workspace_path=retry_entry.workspace_path,
                ),
            )
            return

        # 分派
        self._dispatch_issue(issue, attempt=attempt)

    # ====================================================================
    # 对账
    # ====================================================================

    async def _reconcile_running_issues(self) -> None:
        """对账活跃运行。

        对应规范 §8.5 活跃运行对账，包含两个部分：
        A. 停顿检测
        B. 跟踪器状态刷新
        """
        # 部分 A：停顿检测
        await self._reconcile_stalled_runs()

        # 部分 B：跟踪器状态刷新
        await self._reconcile_tracker_states()

    async def _reconcile_stalled_runs(self) -> None:
        """停顿检测。

        对应规范 §8.5 部分 A：
        - 对于每个运行中的问题，计算 elapsed_ms
        - 基于 last_codex_timestamp（如已看到任何事件），否则 started_at
        - 如果 elapsed_ms > stall_timeout_ms，终止 Worker 并排队重试
        - 如果 stall_timeout_ms <= 0，跳过停顿检测
        """
        stall_timeout_ms = self._config.codex.stall_timeout_ms
        if stall_timeout_ms <= 0:
            return

        now = datetime.now(UTC)
        stalled_ids: list[str] = []

        for issue_id, entry in self.state.running.items():
            # 计算最近活动时间
            last_activity = entry.last_codex_timestamp or entry.started_at
            if last_activity is None:
                continue

            elapsed_ms = (now - last_activity).total_seconds() * 1000
            if elapsed_ms > stall_timeout_ms:
                stalled_ids.append(issue_id)

        for issue_id in stalled_ids:
            entry = self.state.running.get(issue_id)
            if entry is None:
                continue

            log = logger.bind(
                issue_id=issue_id,
                issue_identifier=entry.identifier,
            )
            log.warning("stall_detected_terminating_worker")

            # 终止 worker
            if entry.worker_task is not None and not entry.worker_task.done():
                entry.worker_task.cancel()

    async def _reconcile_tracker_states(self) -> None:
        """跟踪器状态刷新。

        对应规范 §8.5 部分 B 和 §16.3：
        - 获取所有运行中问题 ID 的当前问题状态
        - 终态：终止 Worker 并清理工作区
        - 活跃：更新内存中的问题快照
        - 既非活跃也非终态：终止 Worker 但不清理工作区
        - 如果状态刷新失败，保持 Worker 运行
        """
        running_ids = list(self.state.running.keys())
        if not running_ids:
            return

        try:
            refreshed = await self._tracker.fetch_issue_states_by_ids(running_ids)
        except Exception:
            logger.debug("tracker_refresh_failed_keep_workers")
            return

        terminal_lower = {s.lower() for s in self._config.tracker.terminal_states}
        active_lower = {s.lower() for s in self._config.tracker.active_states}

        for issue in refreshed:
            entry = self.state.running.get(issue.id)
            if entry is None:
                continue

            issue_state_lower = issue.state.lower()
            log = logger.bind(
                issue_id=issue.id,
                issue_identifier=entry.identifier,
                tracker_state=issue.state,
            )

            if issue_state_lower in terminal_lower:
                # 终态：终止 Worker 并清理工作区
                log.info("terminal_state_terminating_and_cleanup")
                await self._terminate_running_issue(
                    issue.id, entry, cleanup_workspace=True
                )
            elif issue_state_lower in active_lower:
                # 活跃：更新内存中的问题状态快照
                log.debug("active_state_updating_snapshot")
                entry.issue_state = issue.state
            else:
                # 既非活跃也非终态：终止 Worker 但不清理工作区
                log.info("non_active_non_terminal_terminating_no_cleanup")
                await self._terminate_running_issue(
                    issue.id, entry, cleanup_workspace=False
                )

    async def _terminate_running_issue(
        self,
        issue_id: str,
        entry: RunningEntry,
        *,
        cleanup_workspace: bool,
    ) -> None:
        """终止运行中的问题。

        Args:
            issue_id: 问题 ID
            entry: 运行条目
            cleanup_workspace: 是否清理工作区
        """
        # 终止 worker task
        if entry.worker_task is not None and not entry.worker_task.done():
            entry.worker_task.cancel()
            try:
                await entry.worker_task
            except (asyncio.CancelledError, Exception):
                pass

        # 更新运行时统计
        elapsed = (datetime.now(UTC) - entry.started_at).total_seconds()
        self.state.codex_totals.seconds_running += elapsed

        # 移除运行条目
        self.state.running.pop(issue_id, None)
        self.state.claimed.discard(issue_id)

        # 清理工作区
        if cleanup_workspace:
            try:
                await self._workspace_manager.cleanup_workspace(entry.identifier)
            except Exception:
                logger.exception(
                    "workspace_cleanup_failed",
                    issue_identifier=entry.identifier,
                )

    # ====================================================================
    # 启动终态清理
    # ====================================================================

    async def _startup_terminal_cleanup(self) -> None:
        """启动终态工作区清理。

        对应规范 §8.6：
        1. 查询跟踪器中处于终态的问题
        2. 移除对应的工作区目录
        3. 如果终态问题获取失败，记录警告并继续启动
        """
        try:
            terminal_issues = await self._tracker.fetch_issues_by_states(
                self._config.tracker.terminal_states
            )
        except Exception:
            logger.warning("startup_terminal_fetch_failed_continuing")
            return

        for issue in terminal_issues:
            if not issue.identifier:
                continue
            try:
                await self._workspace_manager.cleanup_workspace(issue.identifier)
                logger.debug(
                    "startup_cleaned_terminal_workspace",
                    issue_identifier=issue.identifier,
                )
            except Exception:
                logger.warning(
                    "startup_workspace_cleanup_failed",
                    issue_identifier=issue.identifier,
                )

    # ====================================================================
    # 运行时配置刷新
    # ====================================================================

    def _refresh_runtime_config(self) -> None:
        """从最新配置刷新运行时参数（支持 WORKFLOW.md 热重载）。

        配置由 WorkflowStore/Watcher 管理热重载，
        此方法将最新配置值同步到编排器状态。
        """
        self.state.poll_interval_ms = self._config.polling.interval_ms
        self.state.max_concurrent_agents = self._config.agent.max_concurrent_agents

    # ====================================================================
    # 可观测性快照
    # ====================================================================

    def snapshot(self) -> dict[str, Any]:
        """可观测性：生成当前状态快照（供 HTTP API 和仪表板使用）。

        委托 SnapshotGenerator 生成快照，包含：
        - 运行中的 worker 信息
        - 重试队列条目
        - 令牌汇总
        - 配置参数
        - 轮询状态
        """
        from taolib.symphony.observability.snapshot import SnapshotGenerator

        gen = SnapshotGenerator()
        system_snapshot = gen.generate(self.state)
        result = system_snapshot.to_dict()

        # 补充 poll 状态信息
        result["poll_check_in_progress"] = self.state.poll_check_in_progress
        result["next_poll_due_at_ms"] = self.state.next_poll_due_at_ms

        return result

    # ====================================================================
    # 分派验证与主机选择
    # ====================================================================

    def _revalidate_issue_for_dispatch(self, issue: Issue) -> bool:
        """分派前重新验证 Issue 有效性（防竞态调度）。

        在 _dispatch_issue 中调用，确保从 filter_dispatchable 到
        实际分派之间状态未发生变化。

        Args:
            issue: 待验证的问题

        Returns:
            True 表示验证通过，可以分派
        """
        # 再次检查是否已被其他路径分派
        if issue.id in self.state.running:
            return False
        if issue.id in self.state.claimed:
            return False
        if issue.id in self.state.retry_attempts:
            return False

        # 检查是否有基本字段
        return not (not issue.id or not issue.identifier or not issue.title or not issue.state)

    def _select_worker_host(self) -> str | None:
        """SSH 场景下最小负载主机选择。

        从配置的 ssh_hosts 中选择当前运行 worker 数最少的主机。
        本地执行时返回 None。

        Returns:
            选中的主机地址，或 None 表示本地执行
        """
        ssh_hosts = self._config.worker.ssh_hosts
        if not ssh_hosts:
            return None

        # 统计每个主机的当前运行数
        host_counts: dict[str, int] = dict.fromkeys(ssh_hosts, 0)
        for entry in self.state.running.values():
            if entry.worker_host in host_counts:
                host_counts[entry.worker_host] += 1

        # 选择最小负载主机
        min_host = min(ssh_hosts, key=lambda h: host_counts[h])
        return min_host

    # ====================================================================
    # 配置验证
    # ====================================================================

    def _validate_dispatch_config(self) -> None:
        """分派预检验证。

        对应规范 §6.3：
        - tracker.kind 存在且受支持
        - tracker.api_key 在 $ 解析后存在
        - tracker.project_slug 存在（当 tracker.kind == "linear" 时）
        - codex.command 存在且非空

        Raises:
            DispatchValidationError: 验证失败
        """
        reasons: list[str] = []

        # tracker.kind
        if not self._config.tracker.kind:
            reasons.append("tracker.kind is required")
        elif self._config.tracker.kind != "linear":
            reasons.append(
                f"unsupported tracker.kind: {self._config.tracker.kind!r}"
            )

        # tracker.api_key
        if not self._config.tracker.api_key:
            reasons.append("tracker.api_key is required")

        # tracker.project_slug（linear 必须）
        if self._config.tracker.kind == "linear" and not self._config.tracker.project_slug:
            reasons.append("tracker.project_slug is required for linear tracker")

        # codex.command
        if not self._config.codex.command:
            reasons.append("codex.command is required")

        if reasons:
            raise DispatchValidationError(reasons)
