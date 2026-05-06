"""Symphony 调度器 — 候选排序与并发控制。

负责候选问题的优先级排序、全局和每状态的槽位计算、
以及分派资格判断。所有方法均为纯函数，不持有可变状态。

排序规则（规范 §8.2）：
1. priority 升序（1..4 优先；null/未知排最后）
2. created_at 最旧优先
3. identifier 字典序决胜

并发控制（规范 §8.3）：
- 全局限制：available_slots = max(max_concurrent_agents - running_count, 0)
- 每状态限制：max_concurrent_agents_by_state[state]，状态键小写规范化
- 无每状态配置时回退到全局限制
"""

from datetime import datetime

from taolib.symphony.config.schema import AgentConfig
from taolib.symphony.orchestrator.state import OrchestratorState
from taolib.symphony.tracker.models import Issue


class Scheduler:
    """候选排序和并发控制。

    无状态的工具类，所有方法接受 state 参数进行判断。
    对齐规范 §8.2（候选选择规则）和 §8.3（并发控制）。
    """

    def sort_for_dispatch(self, issues: list[Issue]) -> list[Issue]:
        """按分派优先级排序候选问题列表。

        排序键（稳定排序意图）：
        1. priority 升序（1..4 优先；null/未知排最后，映射为 999）
        2. created_at 最旧优先（null 映射为 datetime.max）
        3. identifier 字典序决胜

        Args:
            issues: 候选问题列表

        Returns:
            排序后的新列表（不修改原列表）
        """
        return sorted(
            issues,
            key=lambda i: (
                i.priority if i.priority is not None else 999,
                i.created_at or datetime.max,
                i.identifier,
            ),
        )

    def available_slots(self, state: OrchestratorState) -> int:
        """计算全局可用槽位。

        Args:
            state: 编排器当前状态

        Returns:
            可用槽位数（>= 0）
        """
        return max(state.max_concurrent_agents - len(state.running), 0)

    def available_slots_for_state(
        self,
        issue_state: str,
        state: OrchestratorState,
        config: AgentConfig,
    ) -> int:
        """计算指定状态的可用槽位。

        当 max_concurrent_agents_by_state 中存在该状态的配置时，
        使用该配置的上限；否则回退到全局限制。

        状态键按小写规范化后查找（规范 §5.3.5）。

        Args:
            issue_state: 问题跟踪器状态名称
            state: 编排器当前状态
            config: 智能体配置

        Returns:
            该状态下的可用槽位数（>= 0）
        """
        normalized = issue_state.lower()
        per_state_limit = config.max_concurrent_agents_by_state.get(normalized)

        if per_state_limit is not None:
            # 计算该状态下的当前运行数
            running_in_state = sum(
                1
                for entry in state.running.values()
                if entry.issue_state.lower() == normalized
            )
            return max(per_state_limit - running_in_state, 0)

        # 回退到全局限制
        return self.available_slots(state)

    def should_dispatch(self, issue: Issue, state: OrchestratorState) -> bool:
        """判断是否应分派该 issue。

        检查规则（规范 §8.2 候选选择规则）：
        1. issue 具有 id、identifier、title 和 state
        2. 不已在 running 中
        3. 不已在 claimed 中
        4. 不已在 retry_attempts 中

        注意：Todo 状态的阻塞规则检查需要额外的阻塞项状态信息，
        此处基于 Issue.blocked_by（阻塞方 ID 列表）做保守判断——
        当 blocked_by 非空时，由编排器在分派前通过对账确认阻塞项状态。
        全局和每状态槽位检查由调用方在循环中执行。

        Args:
            issue: 待判断的候选问题
            state: 编排器当前状态

        Returns:
            True 表示应分派
        """
        # 必须具有基本字段
        if not issue.id or not issue.identifier or not issue.title or not issue.state:
            return False

        # 不已在运行中
        if issue.id in state.running:
            return False

        # 不已被声明
        if issue.id in state.claimed:
            return False

        # 不已在重试队列中
        return issue.id not in state.retry_attempts

    def filter_dispatchable(
        self,
        issues: list[Issue],
        state: OrchestratorState,
        config: AgentConfig,
    ) -> list[Issue]:
        """从候选列表中筛选可分派的问题，按优先级排序。

        依次检查全局槽位、每状态槽位和分派资格，
        返回在当前槽位限制下可分派的问题子列表。

        Args:
            issues: 候选问题列表
            state: 编排器当前状态
            config: 智能体配置

        Returns:
            可分派的问题列表（已排序，数量不超过可用槽位）
        """
        sorted_issues = self.sort_for_dispatch(issues)
        dispatchable: list[Issue] = []
        global_slots = self.available_slots(state)

        for issue in sorted_issues:
            if global_slots <= 0:
                break

            if not self.should_dispatch(issue, state):
                continue

            # 每状态槽位检查
            state_slots = self.available_slots_for_state(issue.state, state, config)
            if state_slots <= 0:
                continue

            dispatchable.append(issue)
            global_slots -= 1

        return dispatchable
