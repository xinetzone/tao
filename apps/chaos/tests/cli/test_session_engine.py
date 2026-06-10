"""Session Engine 单元测试。

覆盖 :mod:`taolib.cli._world_engines.session_engine` 的核心 API
（generate_session_id / create_session / load_manifest / save_manifest /
append_event / read_events / acquire_lock / release_lock / is_lock_valid /
load_index）以及 ``world session`` CLI 子命令的端到端集成。
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from taolib.cli._world_engines import session_engine
from taolib.cli._world_engines.session_engine import (
    LockHeldError,
    SessionArchivedError,
    SessionEvent,
    SessionManifest,
    SessionNotFoundError,
    acquire_lock,
    append_event,
    create_session,
    generate_session_id,
    is_lock_valid,
    load_index,
    load_manifest,
    read_events,
    release_lock,
    save_manifest,
)

# tests/cli/test_session_engine.py → tests/cli → tests → <chaos root>
_CHAOS_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def state_dir(tmp_path: Path) -> Path:
    """创建临时 world.state/ 目录结构。"""
    sd = tmp_path / "world.state"
    sd.mkdir()
    return sd


@pytest.fixture
def agents_dir(tmp_path: Path) -> Path:
    """创建包含 world.toml 的临时 .agents/ 目录。"""
    ad = tmp_path / ".agents"
    ad.mkdir()
    (ad / "world.toml").write_text('[world]\nname = "test"\n', encoding="utf-8")
    return ad


# ---------------------------------------------------------------------------
# 1. generate_session_id
# ---------------------------------------------------------------------------


def test_generate_session_id_format() -> None:
    """验证返回格式为 <slug>-<base36>，slug 取 title 前几个词（小写）。"""
    sid = generate_session_id("Hello World Session")
    parts = sid.rsplit("-", 1)
    assert len(parts) == 2
    slug, b36 = parts
    assert slug == "hello-world-session"
    assert b36.isalnum()
    assert 5 <= len(b36) <= 6


def test_generate_session_id_cjk() -> None:
    """验证 CJK 标题能正确生成 slug。"""
    sid = generate_session_id("为帛书《老子》做注疏")
    assert "-" in sid
    b36 = sid.rsplit("-", 1)[1]
    assert 5 <= len(b36) <= 6


# ---------------------------------------------------------------------------
# 2. create_session
# ---------------------------------------------------------------------------


def test_create_session_skeleton(state_dir: Path) -> None:
    """验证目录骨架正确创建（sessions/<id>/manifest.toml, events.toml,
    context.md, artifacts/, lock.toml）。"""
    manifest = create_session(state_dir, "Test Session")
    session_dir = state_dir / "sessions" / manifest.id
    assert session_dir.is_dir()
    assert (session_dir / "manifest.toml").is_file()
    assert (session_dir / "events.toml").is_file()
    assert (session_dir / "context.md").is_file()
    assert (session_dir / "artifacts").is_dir()
    assert (session_dir / "lock.toml").is_file()


def test_create_session_manifest(state_dir: Path) -> None:
    """验证 manifest.toml 内容：state=active, last_event_seq=2。"""
    manifest = create_session(state_dir, "Test Session")
    assert manifest.state == "active"
    assert manifest.last_event_seq == 2
    assert manifest.title == "Test Session"


def test_create_session_events(state_dir: Path) -> None:
    """验证 events.toml 包含 2 条初始事件（session.created + lock.acquired）。"""
    manifest = create_session(state_dir, "Test Session")
    session_dir = state_dir / "sessions" / manifest.id
    events = read_events(session_dir)
    assert len(events) == 2
    assert events[0].type == "session.created"
    assert events[1].type == "lock.acquired"


def test_create_session_lock(state_dir: Path) -> None:
    """验证 lock.toml 内容包含 surface 和 lease_until。"""
    manifest = create_session(state_dir, "Test Session", surface="cli")
    session_dir = state_dir / "sessions" / manifest.id
    lock = session_engine.load_lock(session_dir)
    assert lock is not None
    assert lock.surface == "cli"
    assert lock.lease_until != ""


def test_create_session_index(state_dir: Path) -> None:
    """验证 index.toml 被更新，包含刚创建的 session。"""
    manifest = create_session(state_dir, "Test Session")
    entries = load_index(state_dir)
    assert len(entries) == 1
    assert entries[0]["id"] == manifest.id
    assert entries[0]["state"] == "active"


# ---------------------------------------------------------------------------
# 3. load_manifest / save_manifest
# ---------------------------------------------------------------------------


def test_load_manifest_roundtrip(state_dir: Path) -> None:
    """创建 session 后 load，验证所有字段正确。"""
    manifest = create_session(state_dir, "Roundtrip Test")
    session_dir = state_dir / "sessions" / manifest.id
    loaded = load_manifest(session_dir)
    assert loaded.id == manifest.id
    assert loaded.title == manifest.title
    assert loaded.state == manifest.state
    assert loaded.last_event_seq == manifest.last_event_seq
    assert loaded.created_by == manifest.created_by


def test_save_manifest_persist(state_dir: Path) -> None:
    """修改 state 后 save，再 load 验证持久化。"""
    manifest = create_session(state_dir, "Persist Test")
    session_dir = state_dir / "sessions" / manifest.id
    updated = SessionManifest(
        id=manifest.id,
        title=manifest.title,
        created_by=manifest.created_by,
        created_at=manifest.created_at,
        state="suspended",
        last_event_seq=manifest.last_event_seq,
        last_writer=manifest.last_writer,
        allowed_runtimes=manifest.allowed_runtimes,
        task_id=manifest.task_id,
    )
    save_manifest(session_dir, updated)
    loaded = load_manifest(session_dir)
    assert loaded.state == "suspended"


def test_load_manifest_not_found(tmp_path: Path) -> None:
    """manifest.toml 不存在时抛 SessionNotFoundError。"""
    with pytest.raises(SessionNotFoundError):
        load_manifest(tmp_path / "nonexistent")


# ---------------------------------------------------------------------------
# 3a. manifest / index 特殊字符 round-trip
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title",
    [
        'a"b',              # 双引号
        "a\\b",             # 反斜杠
        "a\nb",             # 换行
        'a"b\\c\nd',        # 混合
        '{"key": "val"}',   # JSON 风格
        "为帛书《老子》做注疏",  # CJK + 书名号
        "a\tb",             # 制表符
        "line1\r\nline2",   # CRLF
    ],
)
def test_create_session_special_title_roundtrip(
    state_dir: Path, title: str
) -> None:
    """特殊字符标题：创建后 load_manifest 可正确读回。"""
    manifest = create_session(state_dir, title)
    session_dir = state_dir / "sessions" / manifest.id
    loaded = load_manifest(session_dir)
    assert loaded.title == title
    assert loaded.id == manifest.id


@pytest.mark.parametrize(
    "task_id",
    [
        'task-"abc"',
        "task\\xyz",
        "task\nwith\nnewlines",
        'task"\\mixed',
        None,
        "",
    ],
)
def test_create_session_special_task_id(
    state_dir: Path, task_id: str | None
) -> None:
    """特殊 task_id：创建后 load_manifest 可正确读回。

    task_id 为空字符串时 manifest 写空串，但 load 时 ``or None`` 会转为 None，
    属于设计行为（TOML 无 null 字面量）。
    """
    manifest = create_session(state_dir, "Normal Title", task_id=task_id)
    session_dir = state_dir / "sessions" / manifest.id
    loaded = load_manifest(session_dir)
    if task_id:
        assert loaded.task_id == task_id
    else:
        # None 和 "" 经 round-trip 后统一为 None
        assert loaded.task_id is None


def test_create_session_special_title_index_roundtrip(
    state_dir: Path,
) -> None:
    """特殊标题 Session 创建后，load_index 可正确读回。"""
    title = 'a"b\\c\nd\te\t"mixed"'
    manifest = create_session(state_dir, title)
    entries = load_index(state_dir)
    assert len(entries) == 1
    assert entries[0]["id"] == manifest.id
    assert entries[0]["title"] == title
    assert entries[0]["state"] == "active"


def test_index_multiple_special_titles(state_dir: Path) -> None:
    """多个特殊标题 Session 共存时，index.toml 全部可解析。"""
    titles = ['a"b', "c\\d", "e\nf", "normal"]
    manifests = [create_session(state_dir, t) for t in titles]
    entries = load_index(state_dir)
    assert len(entries) == 4
    by_id = {e["id"]: e for e in entries}
    for m in manifests:
        assert by_id[m.id]["title"] == m.title


# ---------------------------------------------------------------------------
# 4. append_event
# ---------------------------------------------------------------------------


def test_append_event(state_dir: Path) -> None:
    """追加一条 context.appended 事件，验证 events.toml 现在有 3 条事件，
    manifest.last_event_seq 更新为 3。"""
    manifest = create_session(state_dir, "Append Test")
    session_dir = state_dir / "sessions" / manifest.id
    event = SessionEvent(
        seq=manifest.last_event_seq + 1,
        ts="2026-01-01T00:00:00+08:00",
        surface="cli",
        actor="user",
        type="context.appended",
        payload={"content": "hello"},
    )
    append_event(session_dir, event)
    events = read_events(session_dir)
    assert len(events) == 3
    assert events[-1].type == "context.appended"
    assert events[-1].payload["content"] == "hello"

    loaded = load_manifest(session_dir)
    assert loaded.last_event_seq == 3


# ---------------------------------------------------------------------------
# 5. read_events
# ---------------------------------------------------------------------------


def test_read_events_all(state_dir: Path) -> None:
    """验证返回全部事件。"""
    manifest = create_session(state_dir, "Read Test")
    session_dir = state_dir / "sessions" / manifest.id
    events = read_events(session_dir)
    assert len(events) == 2
    assert events[0].seq == 1
    assert events[1].seq == 2


def test_read_events_tail(state_dir: Path) -> None:
    """验证 tail=1 只返回最后一条。"""
    manifest = create_session(state_dir, "Tail Test")
    session_dir = state_dir / "sessions" / manifest.id
    events = read_events(session_dir, tail=1)
    assert len(events) == 1
    assert events[0].seq == 2


def test_read_events_empty(state_dir: Path) -> None:
    """空 events.toml 返回空列表。"""
    manifest = create_session(state_dir, "Empty Test")
    session_dir = state_dir / "sessions" / manifest.id
    (session_dir / "events.toml").write_text("", encoding="utf-8")
    events = read_events(session_dir)
    assert events == []


# ---------------------------------------------------------------------------
# 6. acquire_lock / release_lock / is_lock_valid
# ---------------------------------------------------------------------------


def test_acquire_after_release(state_dir: Path) -> None:
    """无锁时获取成功：release 后 acquire 成功。"""
    manifest = create_session(state_dir, "Lock Test")
    session_dir = state_dir / "sessions" / manifest.id
    release_lock(session_dir)
    lock = acquire_lock(session_dir, surface="cli")
    assert lock.surface == "cli"
    assert is_lock_valid(session_dir) is True


def test_acquire_lock_held_by_other(state_dir: Path) -> None:
    """有效锁拒绝：未释放时另一个 surface 尝试获取，抛 LockHeldError。"""
    manifest = create_session(state_dir, "Held Test")
    session_dir = state_dir / "sessions" / manifest.id
    with pytest.raises(LockHeldError):
        acquire_lock(session_dir, surface="web")


def test_acquire_expired_lock(state_dir: Path) -> None:
    """过期锁：mock 当前时间为未来，验证可以获取。"""
    manifest = create_session(state_dir, "Expired Test")
    session_dir = state_dir / "sessions" / manifest.id

    far_future = datetime.now(UTC).astimezone() + timedelta(hours=1)

    # datetime 是不可变 C 类型，直接 patch datetime.now 会失败；
    # 因此将 session_engine 模块中的 datetime 整个替换为 mock 对象。
    class MockDatetime:
        @staticmethod
        def now(tz=None):
            return far_future

        fromisoformat = datetime.fromisoformat
        timezone = timezone
        timedelta = timedelta

    with patch(
        "taolib.cli._world_engines.session_engine.datetime",
        MockDatetime(),
    ):
        new_lock = acquire_lock(session_dir, surface="web")
        assert new_lock.surface == "web"


def test_is_lock_valid_after_release(state_dir: Path) -> None:
    """释放后 is_lock_valid 返回 False。"""
    manifest = create_session(state_dir, "Valid Test")
    session_dir = state_dir / "sessions" / manifest.id
    assert is_lock_valid(session_dir) is True
    release_lock(session_dir)
    assert is_lock_valid(session_dir) is False


def test_acquire_lock_archived_session(state_dir: Path) -> None:
    """archived session 禁止加锁，抛 SessionArchivedError。"""
    manifest = create_session(state_dir, "Archived Lock Test")
    session_dir = state_dir / "sessions" / manifest.id
    updated = SessionManifest(
        id=manifest.id,
        title=manifest.title,
        created_by=manifest.created_by,
        created_at=manifest.created_at,
        state="archived",
        last_event_seq=manifest.last_event_seq,
        last_writer=manifest.last_writer,
        allowed_runtimes=manifest.allowed_runtimes,
        task_id=manifest.task_id,
    )
    save_manifest(session_dir, updated)
    with pytest.raises(SessionArchivedError):
        acquire_lock(session_dir, surface="cli")


# ---------------------------------------------------------------------------
# 7. load_index
# ---------------------------------------------------------------------------


def test_load_index_multiple(state_dir: Path) -> None:
    """创建多个 session，验证 index 包含全部。"""
    m1 = create_session(state_dir, "Session One")
    m2 = create_session(state_dir, "Session Two")
    entries = load_index(state_dir)
    ids = {e["id"] for e in entries}
    assert len(entries) == 2
    assert m1.id in ids
    assert m2.id in ids


# ---------------------------------------------------------------------------
# 8. CLI 集成测试
# ---------------------------------------------------------------------------


def _run_world_cli(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """以子进程方式调用 ``python -m taolib.cli.world ...``。"""
    env = os.environ.copy()
    src_dir = str(_CHAOS_ROOT / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_dir + os.pathsep + existing if existing else src_dir
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "taolib.cli.world", *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def test_cli_session_lifecycle(agents_dir: Path) -> None:
    """端到端 CLI 测试：new → list → show → release → resume → release
    → archive → list --state archived。"""
    # new
    result = _run_world_cli(["session", "new", "test task"], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr
    sid = result.stdout.strip().splitlines()[0]
    assert "-" in sid

    # list
    result = _run_world_cli(["session", "list"], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr
    assert sid in result.stdout

    # show
    result = _run_world_cli(["session", "show", sid], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr
    assert "test task" in result.stdout

    # release
    result = _run_world_cli(["session", "release", "--id", sid], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr

    # resume
    result = _run_world_cli(["session", "resume", sid], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr

    # release again
    result = _run_world_cli(["session", "release", "--id", sid], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr

    # archive
    result = _run_world_cli(["session", "archive", sid], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr

    # list --state archived
    result = _run_world_cli(
        ["session", "list", "--state", "archived"], cwd=agents_dir.parent
    )
    assert result.returncode == 0, result.stderr
    assert sid in result.stdout


def test_cli_session_list_state_filter(agents_dir: Path) -> None:
    """验证 --state 过滤逻辑：active 和 archived 互不包含。"""
    result = _run_world_cli(["session", "new", "active task"], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr
    active_sid = result.stdout.strip().splitlines()[0]

    result = _run_world_cli(["session", "new", "archive task"], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr
    archive_sid = result.stdout.strip().splitlines()[0]

    # 释放并归档第二个
    result = _run_world_cli(
        ["session", "release", "--id", archive_sid], cwd=agents_dir.parent
    )
    assert result.returncode == 0, result.stderr
    result = _run_world_cli(["session", "archive", archive_sid], cwd=agents_dir.parent)
    assert result.returncode == 0, result.stderr

    # list --state active 只包含 active_sid
    result = _run_world_cli(
        ["session", "list", "--state", "active"], cwd=agents_dir.parent
    )
    assert result.returncode == 0, result.stderr
    assert active_sid in result.stdout
    assert archive_sid not in result.stdout

    # list --state archived 只包含 archive_sid
    result = _run_world_cli(
        ["session", "list", "--state", "archived"], cwd=agents_dir.parent
    )
    assert result.returncode == 0, result.stderr
    assert archive_sid in result.stdout
    assert active_sid not in result.stdout
