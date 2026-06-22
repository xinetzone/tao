"""角色生命周期事件类型和发射函数。

定义角色激活、切换、权限拒绝和解除激活等事件类型常量，
并提供对应的 WAL 发射辅助函数。
"""

from __future__ import annotations

import logging
from pathlib import Path

from .event_store import append_event, next_event_seq
from .models import SessionEvent
from .time_utils import now_iso

logger = logging.getLogger(__name__)

# 角色生命周期事件类型
ROLE_ACTIVATED = "role.activated"
ROLE_SWITCHED = "role.switched"
ROLE_PERMISSION_DENIED = "role.permission_denied"
ROLE_DEACTIVATED = "role.deactivated"


def emit_role_activated(
    session_dir: Path,
    *,
    role_id: str,
    bindings_loaded: list[str],
    targets_merged: list[str],
    surface: str = "cli",
    actor: str = "agent",
) -> None:
    """记录角色激活事件到 Session WAL。

    Args:
        session_dir: Session 目录路径。
        role_id: 激活的角色 ID。
        bindings_loaded: 已加载的绑定资产路径列表。
        targets_merged: 路由匹配后合并的最终 targets 列表。
        surface: 产生事件的端。
        actor: 操作者。
    """
    event = SessionEvent(
        seq=next_event_seq(session_dir),
        ts=now_iso(),
        surface=surface,
        actor=actor,
        type=ROLE_ACTIVATED,
        payload={
            "role_id": role_id,
            "bindings_loaded": list(bindings_loaded),
            "targets_merged": list(targets_merged),
        },
    )
    append_event(session_dir, event)
    logger.info(
        "emit_role_activated: role_id=%s bindings=%d targets=%d session_dir=%s",
        role_id,
        len(bindings_loaded),
        len(targets_merged),
        session_dir.name,
    )


def emit_role_switched(
    session_dir: Path,
    *,
    from_role: str,
    to_role: str,
    handoff_reason: str = "",
    surface: str = "cli",
    actor: str = "agent",
) -> None:
    """记录角色切换事件到 Session WAL。

    Args:
        session_dir: Session 目录路径。
        from_role: 原角色 ID。
        to_role: 新角色 ID。
        handoff_reason: 切换原因。
        surface: 产生事件的端。
        actor: 操作者。
    """
    event = SessionEvent(
        seq=next_event_seq(session_dir),
        ts=now_iso(),
        surface=surface,
        actor=actor,
        type=ROLE_SWITCHED,
        payload={
            "from_role": from_role,
            "to_role": to_role,
            "handoff_reason": handoff_reason,
        },
    )
    append_event(session_dir, event)
    logger.info(
        "emit_role_switched: from_role=%s to_role=%s reason=%r session_dir=%s",
        from_role,
        to_role,
        handoff_reason,
        session_dir.name,
    )


def emit_role_permission_denied(
    session_dir: Path,
    *,
    role_id: str,
    file_path: str,
    denied_by: str,
    surface: str = "cli",
    actor: str = "agent",
) -> None:
    """记录角色权限拒绝事件到 Session WAL。

    Args:
        session_dir: Session 目录路径。
        role_id: 当前角色 ID。
        file_path: 被拒绝访问的文件路径。
        denied_by: 匹配到的拒绝规则。
        surface: 产生事件的端。
        actor: 操作者。
    """
    event = SessionEvent(
        seq=next_event_seq(session_dir),
        ts=now_iso(),
        surface=surface,
        actor=actor,
        type=ROLE_PERMISSION_DENIED,
        payload={
            "role_id": role_id,
            "file_path": file_path,
            "denied_by": denied_by,
        },
    )
    append_event(session_dir, event)
    logger.warning(
        "emit_role_permission_denied: role_id=%s file=%s denied_by=%s session_dir=%s",
        role_id,
        file_path,
        denied_by,
        session_dir.name,
    )


def emit_role_deactivated(
    session_dir: Path,
    *,
    role_id: str,
    duration_seconds: float = 0.0,
    surface: str = "cli",
    actor: str = "agent",
) -> None:
    """记录角色解除激活事件到 Session WAL。

    Args:
        session_dir: Session 目录路径。
        role_id: 解除的角色 ID。
        duration_seconds: 角色激活持续时长（秒）。
        surface: 产生事件的端。
        actor: 操作者。
    """
    event = SessionEvent(
        seq=next_event_seq(session_dir),
        ts=now_iso(),
        surface=surface,
        actor=actor,
        type=ROLE_DEACTIVATED,
        payload={
            "role_id": role_id,
            "duration_seconds": float(duration_seconds),
        },
    )
    append_event(session_dir, event)
    logger.info(
        "emit_role_deactivated: role_id=%s duration=%.2fs session_dir=%s",
        role_id,
        duration_seconds,
        session_dir.name,
    )
