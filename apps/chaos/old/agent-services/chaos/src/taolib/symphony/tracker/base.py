"""Tracker 抽象基类 — 定义 Issue Tracker 客户端的统一接口。

所有 tracker 实现（Linear、Jira 等）均须实现 ``TrackerClient``，
由编排层通过该接口进行依赖反转。
"""

from abc import ABC, abstractmethod

from taolib.symphony.tracker.models import Issue


class TrackerClient(ABC):
    """Issue Tracker 客户端抽象基类。

    子类需实现以下三个查询方法，供编排层在轮询周期中调用：

    - :meth:`fetch_candidate_issues`  — 获取待处理的候选 issue
    - :meth:`fetch_issues_by_states`  — 按状态集合批量获取 issue
    - :meth:`fetch_issue_states_by_ids` — 根据 ID 批量获取 issue 的当前状态
    """

    @abstractmethod
    async def fetch_candidate_issues(self) -> list[Issue]:
        """获取候选 issue 列表。

        返回当前活跃状态下、属于指定项目的所有 issue，
        用于编排层的调度决策。
        """

    @abstractmethod
    async def fetch_issues_by_states(self, states: list[str]) -> list[Issue]:
        """按状态集合过滤 issue。

        主要用于终态清理（如启动时扫描 Done / Cancelled 状态）。

        Args:
            states: 状态名称列表（大小写敏感，与 tracker 原始值一致）。
        """

    @abstractmethod
    async def fetch_issue_states_by_ids(self, issue_ids: list[str]) -> list[Issue]:
        """根据 ID 列表批量获取 issue 的当前状态。

        用于协调循环（reconciliation）中刷新运行中 issue 的最新状态，
        以检测是否已被外部转为终态。

        Args:
            issue_ids: Issue UUID 列表。
        """
