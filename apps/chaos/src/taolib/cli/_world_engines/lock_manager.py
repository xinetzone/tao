"""租约式悲观锁管理。

负责 ``lock.toml`` 的读写和锁生命周期管理。
"""

from __future__ import annotations

import logging
import os
import tomllib
from datetime import UTC, datetime
from pathlib import Path

from .exceptions import LockHeldError, SessionArchivedError, SessionNotFoundError
from .models import LockInfo
from .time_utils import lease_until_iso, now_iso, parse_iso
from .toml_serializer import format_lock_toml

logger = logging.getLogger(__name__)


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


def is_lease_expired(lock: LockInfo) -> bool:
    """判断锁的租约是否已过期。"""
    try:
        lease_dt = parse_iso(lock.lease_until)
        now_dt = datetime.now(UTC).astimezone()
        return now_dt >= lease_dt
    except (ValueError, TypeError):
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
    return not is_lease_expired(lock)


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
        logger.error("acquire_lock: session_dir not found path=%s", session_dir)
        raise SessionNotFoundError(f"Session directory not found: {session_dir}")

    # 检查 session 是否已归档
    from .session_storage import load_manifest

    manifest_path = session_dir / "manifest.toml"
    if manifest_path.exists():
        try:
            mf = load_manifest(session_dir)
            if mf.state == "archived":
                logger.warning(
                    "acquire_lock: blocked, session archived session_id=%s", mf.id
                )
                raise SessionArchivedError(
                    f"Session '{mf.id}' is archived and cannot be locked."
                )
        except SessionNotFoundError:
            pass

    now_ts = now_iso()
    lease_until = lease_until_iso(lease_minutes)
    instance_id = f"{surface}-{os.getpid()}"
    existing = load_lock(session_dir)

    if existing is None or is_lease_expired(existing):
        action = "created" if existing is None else "replaced (expired)"
        lock = LockInfo(
            surface=surface,
            instance_id=instance_id,
            actor=actor,
            acquired_at=now_ts,
            lease_until=lease_until,
            renew_count=0,
        )
    elif existing.surface == surface:
        action = f"renewed (count={existing.renew_count + 1})"
        lock = LockInfo(
            surface=existing.surface,
            instance_id=existing.instance_id,
            actor=existing.actor,
            acquired_at=existing.acquired_at,
            lease_until=lease_until,
            renew_count=existing.renew_count + 1,
        )
    else:
        if steal and is_lease_expired(existing):
            action = "stolen (expired)"
            lock = LockInfo(
                surface=surface,
                instance_id=instance_id,
                actor=actor,
                acquired_at=now_ts,
                lease_until=lease_until,
                renew_count=0,
            )
        else:
            logger.warning(
                "acquire_lock: denied, lock held by surface=%s instance=%s "
                "lease_until=%s",
                existing.surface,
                existing.instance_id,
                existing.lease_until,
            )
            raise LockHeldError(
                f"Lock is held by '{existing.surface}' (instance: {existing.instance_id}), "
                f"lease until {existing.lease_until}. "
                f"Use steal=True only after lease expires."
            )

    logger.info(
        "acquire_lock: %s session_dir=%s surface=%s instance=%s lease_until=%s",
        action,
        session_dir.name,
        lock.surface,
        lock.instance_id,
        lock.lease_until,
    )
    (session_dir / "lock.toml").write_text(format_lock_toml(lock), encoding="utf-8")
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
