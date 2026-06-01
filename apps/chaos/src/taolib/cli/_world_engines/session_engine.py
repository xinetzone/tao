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
"""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

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

# ---------------------------------------------------------------------------
# 自定义异常
# ---------------------------------------------------------------------------


class SessionError(Exception):
    """Session 操作基础异常。"""


class SessionNotFoundError(SessionError):
    """目标 session 目录或 manifest 不存在。"""


class LockHeldError(SessionError):
    """锁被其他端持有且租约有效。"""


class SessionArchivedError(SessionError):
    """Session 已归档，不可写入。"""


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


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
    payload: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 时间工具
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """返回当前时间的 ISO 8601 with offset 字符串。"""
    return datetime.now(UTC).astimezone().isoformat()


def _parse_iso(ts: str) -> datetime:
    """将 ISO 8601 with offset 字符串解析为 datetime（带时区）。"""
    return datetime.fromisoformat(ts)


def _lease_until_iso(lease_minutes: int) -> str:
    """计算从现在起 lease_minutes 分钟后的 ISO 8601 时间戳。"""
    dt = datetime.now(UTC).astimezone() + timedelta(minutes=lease_minutes)
    return dt.isoformat()


# ---------------------------------------------------------------------------
# session_id 生成
# ---------------------------------------------------------------------------


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
    # 去标点，保留字母、数字、CJK 字符，统一用空格分隔
    cleaned = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", title, flags=re.UNICODE)
    words = cleaned.lower().split()
    slug_parts = words[:3] if words else ["session"]
    slug = "-".join(slug_parts)

    # base36 编码当前时间戳（整秒）
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


# ---------------------------------------------------------------------------
# 目录管理
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# TOML 序列化工具（手工格式化，因标准库 tomllib 只读）
# ---------------------------------------------------------------------------


def _format_manifest_toml(manifest: SessionManifest) -> str:
    """将 SessionManifest 序列化为 manifest.toml 文本。"""
    runtimes = ", ".join(f'"{r}"' for r in manifest.allowed_runtimes)
    # TOML 无 null 字面量；task_id 缺省时写空字符串，加载时再转为 None
    task_id_line = (
        f'task_id = "{manifest.task_id}"' if manifest.task_id else 'task_id = ""'
    )
    return (
        "[session]\n"
        f'id = "{manifest.id}"\n'
        f'title = "{manifest.title}"\n'
        f'created_by = "{manifest.created_by}"\n'
        f'created_at = "{manifest.created_at}"\n'
        'schema_version = "world-session-v1"\n'
        "\n"
        "[session.task]\n"
        f"{task_id_line}\n"
        'parent_session = ""\n'
        "\n"
        "[session.allowed_runtimes]\n"
        f"runtimes = [{runtimes}]\n"
        "\n"
        "[session.status]\n"
        f'state = "{manifest.state}"\n'
        f"last_event_seq = {manifest.last_event_seq}\n"
        f'last_writer = "{manifest.last_writer}"\n'
    )


def _format_lock_toml(lock: LockInfo) -> str:
    """将 LockInfo 序列化为 lock.toml 文本。"""
    return (
        "[holder]\n"
        f'surface = "{lock.surface}"\n'
        f'instance_id = "{lock.instance_id}"\n'
        f'actor = "{lock.actor}"\n'
        "\n"
        "[lease]\n"
        f'acquired_at = "{lock.acquired_at}"\n'
        f'lease_until = "{lock.lease_until}"\n'
        f"renew_count = {lock.renew_count}\n"
    )


def _format_event_block(event: SessionEvent) -> str:
    """将 SessionEvent 序列化为单个 ``[[event]]`` TOML 块文本。

    payload 中每个值根据类型选择合适的 TOML 表示。
    """
    lines: list[str] = [
        "",
        "[[event]]",
        f"seq = {event.seq}",
        f'ts = "{event.ts}"',
        f'surface = "{event.surface}"',
        f'actor = "{event.actor}"',
        f'type = "{event.type}"',
        "",
        "[event.payload]",
    ]
    for k, v in event.payload.items():
        if v is None:
            lines.append(f'{k} = ""')
        elif isinstance(v, bool):
            lines.append(f"{k} = {str(v).lower()}")
        elif isinstance(v, int | float):
            lines.append(f"{k} = {v}")
        elif isinstance(v, list):
            items = ", ".join(f'"{i}"' if isinstance(i, str) else str(i) for i in v)
            lines.append(f"{k} = [{items}]")
        else:
            # 字符串：转义双引号和反斜杠
            escaped = str(v).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{k} = "{escaped}"')
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------


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
    now_ts = _now_iso()

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
    lease_until = _lease_until_iso(lease_minutes)
    instance_id = f"{surface}-{os.getpid()}"
    event_lock = SessionEvent(
        seq=2,
        ts=_now_iso(),
        surface=surface,
        actor=actor,
        type="lock.acquired",
        payload={"holder": instance_id, "lease_until": lease_until},
    )
    append_event(session_dir, event_lock)

    # 7. 写入 lock.toml
    lock = LockInfo(
        surface=surface,
        instance_id=instance_id,
        actor=actor,
        acquired_at=now_ts,
        lease_until=lease_until,
        renew_count=0,
    )
    (session_dir / "lock.toml").write_text(_format_lock_toml(lock), encoding="utf-8")

    # 8. 更新 index.toml（重新加载最新 manifest 以获取正确 last_event_seq）
    final_manifest = load_manifest(session_dir)
    update_index(state_dir, final_manifest)

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

    return SessionManifest(
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


def save_manifest(session_dir: Path, manifest: SessionManifest) -> None:
    """将 manifest 写回 ``manifest.toml``。

    Args:
        session_dir: 单个 session 的目录路径。
        manifest: 要保存的 :class:`SessionManifest` 实例。
    """
    manifest_path = session_dir / "manifest.toml"
    manifest_path.write_text(_format_manifest_toml(manifest), encoding="utf-8")


# ---------------------------------------------------------------------------
# 索引管理
# ---------------------------------------------------------------------------

_INDEX_FILENAME = "index.toml"


def load_index(state_dir: Path) -> list[dict]:
    """从 ``index.toml`` 加载全部 session 索引条目。

    Args:
        state_dir: ``world.state/`` 目录路径。

    Returns:
        索引条目列表（每条为 dict，含 ``id`` / ``title`` / ``state`` /
        ``created_at`` 字段）；文件不存在时返回空列表。
    """
    index_path = state_dir / _INDEX_FILENAME
    if not index_path.exists():
        return []

    with index_path.open("rb") as f:
        data = tomllib.load(f)

    return list(data.get("session", []))


def update_index(state_dir: Path, manifest: SessionManifest) -> None:
    """更新 ``index.toml`` 中对应 session 的条目。

    若该 session_id 已存在则原地更新，否则追加新条目。

    Args:
        state_dir: ``world.state/`` 目录路径。
        manifest: 提供最新状态的 :class:`SessionManifest` 实例。
    """
    entries = load_index(state_dir)

    new_entry = {
        "id": manifest.id,
        "title": manifest.title,
        "state": manifest.state,
        "created_at": manifest.created_at,
    }

    # 查找是否已存在该 ID
    found = False
    for i, entry in enumerate(entries):
        if entry.get("id") == manifest.id:
            entries[i] = new_entry
            found = True
            break
    if not found:
        entries.append(new_entry)

    # 重新生成 index.toml 文本
    lines: list[str] = []
    for entry in entries:
        lines.append("[[session]]")
        lines.append(f'id = "{entry["id"]}"')
        lines.append(f'title = "{entry["title"]}"')
        lines.append(f'state = "{entry["state"]}"')
        lines.append(f'created_at = "{entry["created_at"]}"')
        lines.append("")

    index_path = state_dir / _INDEX_FILENAME
    index_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# 事件 WAL
# ---------------------------------------------------------------------------


def append_event(session_dir: Path, event: SessionEvent) -> None:
    """追加单条事件到 ``events.toml``（WAL，追加模式）。

    事件块以 ``[[event]]`` Array of Tables 格式追加到文件末尾。
    同步更新 ``manifest.toml`` 的 ``last_event_seq`` 和 ``last_writer``。

    Args:
        session_dir: 单个 session 的目录路径。
        event: 要追加的 :class:`SessionEvent` 实例。
    """
    events_path = session_dir / "events.toml"
    block = _format_event_block(event)

    with events_path.open("a", encoding="utf-8") as f:
        f.write(block)

    # 更新 manifest 的 last_event_seq 和 last_writer
    manifest_path = session_dir / "manifest.toml"
    if manifest_path.exists():
        try:
            current = load_manifest(session_dir)
            updated = SessionManifest(
                id=current.id,
                title=current.title,
                created_by=current.created_by,
                created_at=current.created_at,
                state=current.state,
                last_event_seq=event.seq,
                last_writer=event.surface,
                allowed_runtimes=current.allowed_runtimes,
                task_id=current.task_id,
            )
            save_manifest(session_dir, updated)
        except SessionNotFoundError:
            pass


def read_events(
    session_dir: Path,
    *,
    tail: int | None = None,
) -> list[SessionEvent]:
    """读取 ``events.toml`` 中的全部事件。

    Args:
        session_dir: 单个 session 的目录路径。
        tail: 若指定，仅返回最后 N 条事件。

    Returns:
        :class:`SessionEvent` 列表，按 ``seq`` 升序排列。
        文件不存在或为空时返回空列表。
    """
    events_path = session_dir / "events.toml"
    if not events_path.exists():
        return []

    content = events_path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        return []

    raw_events = data.get("event", [])
    result: list[SessionEvent] = []
    for raw in raw_events:
        result.append(
            SessionEvent(
                seq=int(raw.get("seq", 0)),
                ts=raw.get("ts", ""),
                surface=raw.get("surface", ""),
                actor=raw.get("actor", ""),
                type=raw.get("type", ""),
                payload=dict(raw.get("payload", {})),
            )
        )

    result.sort(key=lambda e: e.seq)

    if tail is not None and tail > 0:
        result = result[-tail:]

    return result


# ---------------------------------------------------------------------------
# 锁管理
# ---------------------------------------------------------------------------


def load_lock(session_dir: Path) -> LockInfo | None:
    """加载 ``lock.toml``，不存在时返回 ``None``。

    Args:
        session_dir: 单个 session 的目录路径。

    Returns:
        解析后的 :class:`LockInfo` 实例，或 ``None``（文件不存在时）。
    """
    lock_path = session_dir / "lock.toml"
    if not lock_path.exists():
        return None

    with lock_path.open("rb") as f:
        data = tomllib.load(f)

    holder = data.get("holder", {})
    lease = data.get("lease", {})

    return LockInfo(
        surface=holder.get("surface", ""),
        instance_id=holder.get("instance_id", ""),
        actor=holder.get("actor", ""),
        acquired_at=lease.get("acquired_at", ""),
        lease_until=lease.get("lease_until", ""),
        renew_count=int(lease.get("renew_count", 0)),
    )


def _is_lease_expired(lock: LockInfo) -> bool:
    """判断锁的租约是否已过期。"""
    try:
        lease_dt = _parse_iso(lock.lease_until)
        now_dt = datetime.now(UTC).astimezone()
        return now_dt >= lease_dt
    except ValueError, TypeError:
        # 无法解析时视为过期
        return True


def is_lock_valid(session_dir: Path) -> bool:
    """检查 ``lock.toml`` 是否存在且租约未过期。

    Args:
        session_dir: 单个 session 的目录路径。

    Returns:
        ``True`` 表示锁存在且有效；``False`` 表示不存在或已过期。
    """
    lock = load_lock(session_dir)
    if lock is None:
        return False
    return not _is_lease_expired(lock)


def acquire_lock(
    session_dir: Path,
    *,
    surface: str = "cli",
    actor: str = "user",
    lease_minutes: int = 10,
    steal: bool = False,
) -> LockInfo:
    """获取 Session 写锁（租约式悲观锁）。

    锁获取规则：

    - 锁不存在：直接创建新锁。
    - 锁已过期：直接覆盖。
    - 锁有效且是本端（surface 相同）：续约，``renew_count += 1``。
    - 锁有效且非本端：

      - ``steal=False``：抛出 :class:`LockHeldError`。
      - ``steal=True`` 且锁已过期：覆盖；若锁仍有效则仍抛出 :class:`LockHeldError`。

    Args:
        session_dir: 单个 session 的目录路径。
        surface: 请求锁的端标识。
        actor: 操作者标识。
        lease_minutes: 租约时长（分钟）。
        steal: 是否强制夺锁（仅当锁已过期时有效）。

    Returns:
        获取或续约后的 :class:`LockInfo` 实例。

    Raises:
        LockHeldError: 锁被其他有效端持有且 ``steal=False``（或锁仍有效）。
        SessionNotFoundError: ``session_dir`` 不存在。
        SessionArchivedError: Session 已归档，禁止加锁。
    """
    if not session_dir.exists():
        raise SessionNotFoundError(f"Session directory not found: {session_dir}")

    # 检查 session 是否已归档
    manifest_path = session_dir / "manifest.toml"
    if manifest_path.exists():
        try:
            mf = load_manifest(session_dir)
            if mf.state == "archived":
                raise SessionArchivedError(
                    f"Session '{mf.id}' is archived and cannot be locked."
                )
        except SessionNotFoundError:
            pass

    now_ts = _now_iso()
    lease_until = _lease_until_iso(lease_minutes)
    instance_id = f"{surface}-{os.getpid()}"
    existing = load_lock(session_dir)

    if existing is None:
        # 锁不存在：直接创建
        lock = LockInfo(
            surface=surface,
            instance_id=instance_id,
            actor=actor,
            acquired_at=now_ts,
            lease_until=lease_until,
            renew_count=0,
        )
    elif _is_lease_expired(existing):
        # 锁已过期：直接覆盖
        lock = LockInfo(
            surface=surface,
            instance_id=instance_id,
            actor=actor,
            acquired_at=now_ts,
            lease_until=lease_until,
            renew_count=0,
        )
    elif existing.surface == surface:
        # 锁有效且是本端：续约
        lock = LockInfo(
            surface=existing.surface,
            instance_id=existing.instance_id,
            actor=existing.actor,
            acquired_at=existing.acquired_at,
            lease_until=lease_until,
            renew_count=existing.renew_count + 1,
        )
    else:
        # 锁有效且非本端
        if steal and _is_lease_expired(existing):
            lock = LockInfo(
                surface=surface,
                instance_id=instance_id,
                actor=actor,
                acquired_at=now_ts,
                lease_until=lease_until,
                renew_count=0,
            )
        else:
            raise LockHeldError(
                f"Lock is held by '{existing.surface}' (instance: {existing.instance_id}), "
                f"lease until {existing.lease_until}. "
                f"Use steal=True only after lease expires."
            )

    (session_dir / "lock.toml").write_text(_format_lock_toml(lock), encoding="utf-8")
    return lock


def release_lock(session_dir: Path) -> None:
    """释放写锁：删除 ``lock.toml``。

    若 ``lock.toml`` 不存在，静默忽略（幂等操作）。

    Args:
        session_dir: 单个 session 的目录路径。
    """
    lock_path = session_dir / "lock.toml"
    if lock_path.exists():
        lock_path.unlink()


# ---------------------------------------------------------------------------
# 角色生命周期事件类型
# ---------------------------------------------------------------------------

ROLE_ACTIVATED = "role.activated"
ROLE_SWITCHED = "role.switched"
ROLE_PERMISSION_DENIED = "role.permission_denied"
ROLE_DEACTIVATED = "role.deactivated"


# ---------------------------------------------------------------------------
# 角色生命周期事件辅助函数
# ---------------------------------------------------------------------------


def _next_event_seq(session_dir: Path) -> int:
    """读取 manifest，返回下一条事件的 seq（``last_event_seq + 1``）。

    若 manifest 不存在或读取失败，则退化为 ``1``。
    """
    try:
        return load_manifest(session_dir).last_event_seq + 1
    except SessionNotFoundError:
        return 1


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
        seq=_next_event_seq(session_dir),
        ts=_now_iso(),
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
        seq=_next_event_seq(session_dir),
        ts=_now_iso(),
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
        seq=_next_event_seq(session_dir),
        ts=_now_iso(),
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
        seq=_next_event_seq(session_dir),
        ts=_now_iso(),
        surface=surface,
        actor=actor,
        type=ROLE_DEACTIVATED,
        payload={
            "role_id": role_id,
            "duration_seconds": float(duration_seconds),
        },
    )
    append_event(session_dir, event)
