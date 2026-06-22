"""Session Engine 数据模型定义。

提供 :class:`SessionManifest`、:class:`LockInfo`、:class:`SessionEvent`
三个不可变数据类，不包含任何业务逻辑。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SessionManifest:
    """会话元数据，对应 ``manifest.toml`` 内容。

    Attributes:
        id: 全局唯一 session_id（``<topic-slug>-<timestamp-base36>``）。
        title: 会话标题，自由文本。
        created_by: 创建端标识（``cli`` / ``web`` / ``ide-skill`` / ``api``）。
        created_at: 创建时间，ISO 8601 with offset。
        state: 生命周期状态（``active`` / ``suspended`` / ``archived``）。
        last_event_seq: 最近一条事件的 seq。
        last_writer: 最近写入端标识。
        allowed_runtimes: 允许接入的端列表。
        task_id: 可选的长任务 ID。
    """

    id: str
    title: str
    created_by: str
    created_at: str
    state: str
    last_event_seq: int
    last_writer: str
    allowed_runtimes: list[str] = field(default_factory=list)
    task_id: str | None = None


@dataclass(frozen=True)
class LockInfo:
    """锁租约信息，对应 ``lock.toml`` 内容。

    Attributes:
        surface: 持锁端（``cli`` / ``web`` / ``ide-skill`` / ``api``）。
        instance_id: 端实例唯一标识。
        actor: 操作者标识（如 ``user`` / ``agent`` / ``user@local``）。
        acquired_at: 获取锁时间，ISO 8601 with offset。
        lease_until: 租约过期时间，ISO 8601 with offset。
        renew_count: 续约次数。
    """

    surface: str
    instance_id: str
    actor: str
    acquired_at: str
    lease_until: str
    renew_count: int = 0


@dataclass(frozen=True)
class SessionEvent:
    """单条 Session 事件，对应 ``events.toml`` 中的 ``[[event]]`` 块。

    Attributes:
        seq: 单调递增序号（从 1 开始）。
        ts: 事件时间戳，ISO 8601 with offset（仅供人类阅读，不作排序）。
        surface: 产生事件的端标识。
        actor: 操作者标识。
        type: 事件类型（如 ``session.created`` / ``lock.acquired`` 等）。
        payload: 事件附加数据字典。
    """

    seq: int
    ts: str
    surface: str
    actor: str
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
