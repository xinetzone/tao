"""Session 索引管理。

负责 ``index.toml`` 的读写和维护。
"""

from __future__ import annotations

import logging
import tomllib
from pathlib import Path

from .models import SessionManifest
from .toml_serializer import toml_basic_string

logger = logging.getLogger(__name__)

_INDEX_FILENAME = "index.toml"


def load_index(state_dir: Path) -> list[dict]:  # type: ignore[type-arg]
    """从 ``index.toml`` 加载全部 session 索引条目。

    Args:
        state_dir: ``world.state/`` 目录路径。

    Returns:
        索引条目列表（每条为 dict，含 ``id`` / ``title`` / ``state`` /
        ``created_at`` 字段）；文件不存在时返回空列表。
    """
    index_path = state_dir / _INDEX_FILENAME
    if not index_path.exists():
        logger.debug("load_index: no index file at %s", index_path)
        return []

    with index_path.open("rb") as f:
        data = tomllib.load(f)

    entries = list(data.get("session", []))
    logger.debug("load_index: loaded %d entries", len(entries))
    return entries


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

    found = False
    for i, entry in enumerate(entries):
        if entry.get("id") == manifest.id:
            entries[i] = new_entry
            found = True
            break
    if not found:
        entries.append(new_entry)

    lines: list[str] = []
    for entry in entries:
        lines.append("[[session]]")
        lines.append(f"id = {toml_basic_string(entry['id'])}")
        lines.append(f"title = {toml_basic_string(entry['title'])}")
        lines.append(f"state = {toml_basic_string(entry['state'])}")
        lines.append(f"created_at = {toml_basic_string(entry['created_at'])}")
        lines.append("")

    index_path = state_dir / _INDEX_FILENAME
    index_path.write_text("\n".join(lines), encoding="utf-8")
    logger.debug(
        "update_index: session_id=%s state=%s total_entries=%d",
        manifest.id,
        manifest.state,
        len(entries),
    )
