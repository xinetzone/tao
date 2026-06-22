"""Session Engine：World Session 核心模块。

本模块实现 ``world-session-spec.md`` Draft v0.1 描述的 Session 生命周期管理：
创建、加载、索引、事件追加（WAL）、锁管理（租约式悲观锁）。

文件布局（位于 ``.agents/world.state/`` 下）：

- ``index.toml``：全部 session 索引（``[[session]]`` Array of Tables）
- ``sessions/<id>/manifest.toml``：会话元数据
- ``sessions/<id>/events.toml``：WAL 追加事件流（真相源）
- ``sessions/<id>/context.md``：当前上下文投影（人可读）
- ``sessions/<id>/artifacts/``：中间产物目录
- ``sessions/<id>/lock.toml``：当前持有端的租约

仅依赖标准库（``tomllib`` / ``pathlib`` / ``datetime`` / ``dataclasses`` /
``re`` / ``os``）。

..  note::
    本模块在 ``v0.9`` 重构为统一导出层，实际实现拆分为以下子模块：

    - :mod:`.models` — 数据模型定义
    - :mod:`.exceptions` — 自定义异常
    - :mod:`.time_utils` — 时间工具函数
    - :mod:`.toml_serializer` — TOML 序列化
    - :mod:`.session_storage` — Session CRUD 与存储抽象
    - :mod:`.index_manager` — 全局索引管理
    - :mod:`.event_store` — 事件 WAL 存储
    - :mod:`.lock_manager` — 租约式悲观锁管理
    - :mod:`.role_events` — 角色生命周期事件
"""

from __future__ import annotations

# 事件 WAL
from .event_store import append_event, read_events

# 自定义异常
from .exceptions import (
    LockHeldError,
    SessionArchivedError,
    SessionError,
    SessionNotFoundError,
)

# 索引管理
from .index_manager import load_index, update_index

# 锁管理
from .lock_manager import acquire_lock, is_lock_valid, load_lock, release_lock

# 数据模型
from .models import LockInfo, SessionEvent, SessionManifest

# 角色生命周期事件
from .role_events import (
    ROLE_ACTIVATED,
    ROLE_DEACTIVATED,
    ROLE_PERMISSION_DENIED,
    ROLE_SWITCHED,
    emit_role_activated,
    emit_role_deactivated,
    emit_role_permission_denied,
    emit_role_switched,
)

# Session CRUD & 工具
from .session_storage import (
    create_session,
    ensure_state_dir,
    generate_session_id,
    load_manifest,
    save_manifest,
)

# 时间工具
from .time_utils import lease_until_iso, now_iso, parse_iso

__all__ = [
    # 数据模型
    "SessionManifest",
    "LockInfo",
    "SessionEvent",
    # 自定义异常
    "SessionError",
    "SessionNotFoundError",
    "LockHeldError",
    "SessionArchivedError",
    # 工具函数
    "generate_session_id",
    "ensure_state_dir",
    "now_iso",
    "parse_iso",
    "lease_until_iso",
    # Session CRUD
    "create_session",
    "load_manifest",
    "save_manifest",
    # 索引
    "load_index",
    "update_index",
    # 事件 WAL
    "append_event",
    "read_events",
    # 锁管理
    "acquire_lock",
    "release_lock",
    "is_lock_valid",
    "load_lock",
    # 角色生命周期事件类型
    "ROLE_ACTIVATED",
    "ROLE_SWITCHED",
    "ROLE_PERMISSION_DENIED",
    "ROLE_DEACTIVATED",
    # 角色生命周期事件辅助函数
    "emit_role_activated",
    "emit_role_switched",
    "emit_role_permission_denied",
    "emit_role_deactivated",
]
