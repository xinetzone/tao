"""Tracker 领域模型 — Issue 实体与配置定义。"""

from datetime import datetime

from pydantic import BaseModel, Field


class Issue(BaseModel):
    """规范化后的 Issue 领域模型。

    由 Linear 等外部 tracker 返回的原始数据经 normalize 后得到统一结构，
    供编排层、模板渲染和可观测性输出使用。
    """

    id: str
    identifier: str
    title: str
    description: str | None = None
    priority: int | None = Field(
        default=None,
        description="优先级 1-4，非整数映射为 None",
    )
    url: str | None = None
    state: str
    labels: list[str] = Field(
        default_factory=list,
        description="已转为小写的标签列表",
    )
    blocked_by: list[str] = Field(
        default_factory=list,
        description="阻塞方 issue ID 列表",
    )
    branch_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TrackerConfig(BaseModel):
    """Tracker 客户端配置。

    从 WORKFLOW.md front matter 的 tracker 段解析而来，
    也可由环境变量覆盖。
    """

    kind: str = "linear"
    """Tracker 类型，当前仅支持 ``linear``。"""

    api_key: str
    """Linear API Key，通常以 ``lin_api_`` 开头。"""

    endpoint: str = "https://api.linear.app/graphql"
    """GraphQL 端点地址。"""

    project_slug: str
    """项目 slug，用于候选 issue 的过滤条件。"""

    active_states: list[str] = Field(
        default_factory=lambda: ["Triage", "Backlog", "Todo", "In Progress"],
        description="候选 issue 的活跃状态集合",
    )

    timeout: float = 30.0
    """HTTP 请求超时（秒）。"""

    max_retries: int = 3
    """传输层最大重试次数。"""
