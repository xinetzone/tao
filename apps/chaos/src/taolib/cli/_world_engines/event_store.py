"""事件 WAL（Write-Ahead Log）存储。

负责 ``events.toml`` 的追加和读取。
"""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path

from .models import SessionEvent, SessionManifest
from .toml_serializer import format_event_block

logger = logging.getLogger(__name__)


def append_event(session_dir: Path, event: SessionEvent) -> None:
    """追加单条事件到 ``events.toml``（WAL，追加模式）。

    事件块以 ``[[event]]`` Array of Tables 格式追加到文件末尾。
    同步更新 ``manifest.toml`` 的 ``last_event_seq`` 和 ``last_writer``。

    Args:
        session_dir: 单个 session 的目录路径。
        event: 要追加的 :class:`SessionEvent` 实例。
    """
    events_path = session_dir / "events.toml"
    block = format_event_block(event)

    with events_path.open("a", encoding="utf-8") as f:
        f.write(block)

    logger.debug(
        "append_event: session_dir=%s seq=%d type=%s",
        session_dir.name,
        event.seq,
        event.type,
    )

    # 更新 manifest 的 last_event_seq 和 last_writer
    manifest_path = session_dir / "manifest.toml"
    if manifest_path.exists():
        from .session_storage import load_manifest, save_manifest

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
        except Exception:
            logger.warning(
                "append_event: failed to update manifest after event seq=%d, "
                "session_dir=%s",
                event.seq,
                session_dir,
                exc_info=True,
            )


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
        logger.debug("read_events: no events file, session_dir=%s", session_dir.name)
        return []

    content = events_path.read_text(encoding="utf-8").strip()
    if not content:
        logger.debug("read_events: empty events file, session_dir=%s", session_dir.name)
        return []

    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        logger.warning(
            "read_events: TOML decode error, session_dir=%s", session_dir, exc_info=True
        )
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

    logger.debug("read_events: session_dir=%s count=%d", session_dir.name, len(result))
    return result


def next_event_seq(session_dir: Path) -> int:
    """读取 manifest，返回下一条事件的 seq（``last_event_seq + 1``）。

    若 manifest 不存在或读取失败，则退化为 ``1``。
    """
    from .session_storage import load_manifest

    try:
        return load_manifest(session_dir).last_event_seq + 1
    except Exception:
        return 1
