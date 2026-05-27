"""Symphony 配置模型。

基于 Pydantic v2 定义完整的配置类型层次结构，
覆盖跟踪器、轮询、工作区、钩子、Agent、Codex、Worker 和 Server 配置。
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------


class TrackerConfig(BaseModel):
    """问题跟踪器配置。"""

    kind: Literal["linear"] = "linear"
    endpoint: str = "https://api.linear.app/graphql"
    api_key: str = ""
    project_slug: str = ""
    active_states: list[str] = Field(default=["Todo", "In Progress"])
    terminal_states: list[str] = Field(
        default=["Closed", "Cancelled", "Canceled", "Duplicate", "Done"],
    )


# ---------------------------------------------------------------------------
# Polling
# ---------------------------------------------------------------------------


class PollingConfig(BaseModel):
    """轮询配置。"""

    interval_ms: int = Field(default=30000, ge=1000)


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------


class WorkspaceConfig(BaseModel):
    """工作区配置。"""

    root: Path = Field(default=Path("/tmp/symphony_workspaces"))


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


class HooksConfig(BaseModel):
    """工作区钩子配置。"""

    after_create: str | None = None
    before_run: str | None = None
    after_run: str | None = None
    before_remove: str | None = None
    timeout_ms: int = Field(default=60000, ge=0)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


class AgentConfig(BaseModel):
    """Agent 并发与重试配置。"""

    max_concurrent_agents: int = Field(default=10, ge=1)
    max_turns: int = Field(default=20, ge=1)
    max_retry_backoff_ms: int = Field(default=300000, ge=0)
    max_concurrent_agents_by_state: dict[str, int] = Field(default_factory=dict)

    @field_validator("max_concurrent_agents_by_state", mode="before")
    @classmethod
    def _normalize_state_keys(cls, v: dict[str, int]) -> dict[str, int]:
        """将状态键归一化为小写，并过滤无效条目。"""
        normalized: dict[str, int] = {}
        for key, value in v.items():
            if isinstance(value, int) and value > 0:
                normalized[key.lower()] = value
        return normalized


# ---------------------------------------------------------------------------
# Codex
# ---------------------------------------------------------------------------


class CodexConfig(BaseModel):
    """Codex app-server 配置。"""

    command: str = "codex app-server"
    approval_policy: str | None = None
    thread_sandbox: str | None = None
    turn_sandbox_policy: str | None = None
    turn_timeout_ms: int = Field(default=3600000, ge=0)
    read_timeout_ms: int = Field(default=5000, ge=0)
    stall_timeout_ms: int = Field(default=300000, ge=0)


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------


class WorkerConfig(BaseModel):
    """SSH Worker 扩展配置。"""

    ssh_hosts: list[str] = Field(default_factory=list)
    max_concurrent_agents_per_host: int | None = None


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


class ServerConfig(BaseModel):
    """HTTP Server 扩展配置。"""

    port: int | None = None
    bind: str = "127.0.0.1"


# ---------------------------------------------------------------------------
# Top-level
# ---------------------------------------------------------------------------


class SymphonyConfig(BaseModel):
    """Symphony 编排服务完整配置。"""

    tracker: TrackerConfig = Field(default_factory=TrackerConfig)
    polling: PollingConfig = Field(default_factory=PollingConfig)
    workspace: WorkspaceConfig = Field(default_factory=WorkspaceConfig)
    hooks: HooksConfig = Field(default_factory=HooksConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    codex: CodexConfig = Field(default_factory=CodexConfig)
    worker: WorkerConfig = Field(default_factory=WorkerConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
