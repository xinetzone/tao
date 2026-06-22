"""Session 存储抽象层。

提供 Session CRUD、session_id 生成和目录管理。
"""

from __future__ import annotations

import logging
import os
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from .exceptions import SessionNotFoundError
from .models import SessionEvent, SessionManifest
from .time_utils import lease_until_iso, now_iso
from .toml_serializer import format_lock_toml, format_manifest_toml

logger = logging.getLogger(__name__)


def generate_session_id(title: str) -> str:
    """生成 ``<topic-slug>-<timestamp-base36>`` 格式的 session_id。

    slug 取 title 前 3 个词（小写、去标点、用 ``-`` 连接）。
    timestamp 用当前时间戳（整秒）的 base36 编码（5-6 字符）。

    Args:
        title: 会话标题，任意自由文本。

    Returns:
        格式为 ``word1-word2-word3-<base36ts>`` 的 session_id。

    Examples:
        >>> sid = generate_session_id("为帛书《老子》做注疏")
        >>> "-" in sid
        True
    """
    cleaned = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", title, flags=re.UNICODE)
    words = cleaned.lower().split()
    slug_parts = words[:3] if words else ["session"]
    slug = "-".join(slug_parts)

    ts_int = int(datetime.now(UTC).timestamp())
    base36_chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if ts_int == 0:
        b36 = "0"
    else:
        digits: list[str] = []
        n = ts_int
        while n:
            digits.append(base36_chars[n % 36])
            n //= 36
        b36 = "".join(reversed(digits))

    return f"{slug}-{b36}"


def ensure_state_dir(agents_dir: Path) -> Path:
    """确保 ``.agents/world.state/`` 目录存在，返回其路径。

    Args:
        agents_dir: ``.agents/`` 目录的路径。

    Returns:
        ``world.state/`` 目录路径（已创建）。
    """
    state_dir = agents_dir / "world.state"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "sessions").mkdir(exist_ok=True)
    return state_dir


def create_session(
    state_dir: Path,
    title: str,
    *,
    surface: str = "cli",
    actor: str = "user",
    task_id: str | None = None,
    lease_minutes: int = 10,
    allowed_runtimes: list[str] | None = None,
) -> SessionManifest:
    """新建 Session，创建目录骨架并写入初始文件。

    执行步骤：

    1. 生成 ``session_id``
    2. 创建目录骨架（``sessions/<id>/`` + 子文件 + ``artifacts/``）
    3. 写入 ``manifest.toml``（含 ``session.created`` 前的初始状态）
    4. 追加 ``session.created`` 事件
    5. 追加 ``lock.acquired`` 事件
    6. 写入 ``lock.toml``
    7. 更新 ``index.toml``
    8. 返回 :class:`SessionManifest`

    Args:
        state_dir: ``world.state/`` 目录路径。
        title: 会话标题。
        surface: 创建端标识，默认 ``"cli"``。
        actor: 操作者标识，默认 ``"user"``。
        task_id: 可选的长任务 ID。
        lease_minutes: 锁租约时长（分钟），默认 10。
        allowed_runtimes: 允许接入的端列表；默认为全部四种端。

    Returns:
        已创建的 :class:`SessionManifest` 实例。
    """
    if allowed_runtimes is None:
        allowed_runtimes = ["cli", "web", "ide-skill", "api"]

    session_id = generate_session_id(title)
    now_ts = now_iso()

    logger.info(
        "create_session: session_id=%s title=%r surface=%s actor=%s",
        session_id,
        title,
        surface,
        actor,
    )

    # 1. 创建目录骨架
    session_dir = state_dir / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "artifacts").mkdir(exist_ok=True)

    # 2. 初始化空 events.toml（占位，后续 append_event 追加）
    events_path = session_dir / "events.toml"
    if not events_path.exists():
        events_path.write_text("", encoding="utf-8")

    # 3. 初始化空 context.md
    context_path = session_dir / "context.md"
    if not context_path.exists():
        context_path.write_text(
            f"# {title}\n\n> Session: `{session_id}`\n",
            encoding="utf-8",
        )

    # 4. 写入初始 manifest（last_event_seq=0，后续随 append_event 更新）
    manifest = SessionManifest(
        id=session_id,
        title=title,
        created_by=surface,
        created_at=now_ts,
        state="active",
        last_event_seq=0,
        last_writer=surface,
        allowed_runtimes=allowed_runtimes,
        task_id=task_id,
    )
    save_manifest(session_dir, manifest)

    # 5. 追加 session.created 事件
    from .event_store import append_event

    event_created = SessionEvent(
        seq=1,
        ts=now_ts,
        surface=surface,
        actor=actor,
        type="session.created",
        payload={"title": title, **({"task_id": task_id} if task_id else {})},
    )
    append_event(session_dir, event_created)

    # 6. 追加 lock.acquired 事件
    lease_until = lease_until_iso(lease_minutes)
    instance_id = f"{surface}-{os.getpid()}"
    event_lock = SessionEvent(
        seq=2,
        ts=now_iso(),
        surface=surface,
        actor=actor,
        type="lock.acquired",
        payload={"holder": instance_id, "lease_until": lease_until},
    )
    append_event(session_dir, event_lock)

    # 7. 写入 lock.toml
    from .models import LockInfo

    lock = LockInfo(
        surface=surface,
        instance_id=instance_id,
        actor=actor,
        acquired_at=now_ts,
        lease_until=lease_until,
        renew_count=0,
    )
    (session_dir / "lock.toml").write_text(format_lock_toml(lock), encoding="utf-8")

    # 8. 更新 index.toml（重新加载最新 manifest 以获取正确 last_event_seq）
    final_manifest = load_manifest(session_dir)
    from .index_manager import update_index

    update_index(state_dir, final_manifest)

    logger.info(
        "create_session: done session_id=%s state=%s last_event_seq=%d",
        final_manifest.id,
        final_manifest.state,
        final_manifest.last_event_seq,
    )
    return final_manifest


def load_manifest(session_dir: Path) -> SessionManifest:
    """从 ``manifest.toml`` 加载 session 元数据。

    Args:
        session_dir: 单个 session 的目录路径（``sessions/<id>/``）。

    Returns:
        解析后的 :class:`SessionManifest` 实例。

    Raises:
        SessionNotFoundError: ``manifest.toml`` 不存在。
    """
    manifest_path = session_dir / "manifest.toml"
    if not manifest_path.exists():
        raise SessionNotFoundError(f"manifest.toml not found: {manifest_path}")

    with manifest_path.open("rb") as f:
        data = tomllib.load(f)

    s = data.get("session", {})
    status = s.get("status", {})
    task_section = s.get("task", {})
    runtimes_section = s.get("allowed_runtimes", {})

    allowed = list(runtimes_section.get("runtimes", []))
    task_id = task_section.get("task_id") or None

    result = SessionManifest(
        id=s.get("id", ""),
        title=s.get("title", ""),
        created_by=s.get("created_by", ""),
        created_at=s.get("created_at", ""),
        state=status.get("state", "active"),
        last_event_seq=int(status.get("last_event_seq", 0)),
        last_writer=status.get("last_writer", ""),
        allowed_runtimes=allowed,
        task_id=task_id,
    )
    logger.debug(
        "load_manifest: session_id=%s state=%s last_event_seq=%d",
        result.id,
        result.state,
        result.last_event_seq,
    )
    return result


def save_manifest(session_dir: Path, manifest: SessionManifest) -> None:
    """将 manifest 写回 ``manifest.toml``。

    Args:
        session_dir: 单个 session 的目录路径。
        manifest: 要保存的 :class:`SessionManifest` 实例。
    """
    manifest_path = session_dir / "manifest.toml"
    manifest_path.write_text(format_manifest_toml(manifest), encoding="utf-8")
    logger.debug("save_manifest: session_id=%s state=%s", manifest.id, manifest.state)
