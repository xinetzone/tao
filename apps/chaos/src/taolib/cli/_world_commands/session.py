"""``world session`` 子命令组：World Session 生命周期管理。

根据 ``world-session-spec.md`` Draft v0.1 描述的 CLI 接口规格，
本模块实现 session 子命令族（new / list / show / resume / release /
archive / log），通过调用 :mod:`taolib.cli._world_engines.session_engine`
完成实际操作。

示例::

    $ world session new "为帛书《老子》做注疏" --lease 20
    laozi-session-abc123

    $ world session list --state active
    ID                       TITLE                    STATE      CREATED_AT
    laozi-session-abc123     为帛书《老子》做注疏     active     2026-05-28T10:00:00+08:00

错误码规约：
    WS001 - session 不存在
    WS002 - session 已归档
    WS101 - 锁被他端持有
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC
from pathlib import Path

from taolib.cli._world_engines import session_engine

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------


def _find_state_dir() -> Path:
    """从 cwd 向上查找 ``.agents/world.toml``，返回 ``.agents/world.state/`` 路径。

    沿当前目录逐级向父目录遍历，找到包含 ``.agents/world.toml`` 的目录后，
    在同级 ``.agents/`` 下确保 ``world.state/`` 目录存在并返回其路径。

    Returns:
        ``.agents/world.state/`` 目录的绝对路径（已确保存在）。

    Exits:
        若未找到 ``world.toml`` 则向 stderr 输出错误并以退出码 1 终止。
    """
    current = Path.cwd().resolve()
    for directory in [current, *current.parents]:
        candidate = directory / ".agents" / "world.toml"
        if candidate.is_file():
            agents_dir = candidate.parent
            return session_engine.ensure_state_dir(agents_dir)

    print(
        "错误：在当前目录及其所有父目录中均未找到 .agents/world.toml",
        file=sys.stderr,
    )
    sys.exit(1)


def _format_table_row(
    sid: str,
    title: str,
    state: str,
    created_at: str,
    *,
    id_width: int = 28,
    title_width: int = 28,
    state_width: int = 12,
) -> str:
    """格式化单行表格输出。

    Args:
        sid: Session ID。
        title: 会话标题。
        state: 状态字符串。
        created_at: 创建时间 ISO 字符串。
        id_width: ID 列宽。
        title_width: 标题列宽。
        state_width: 状态列宽。

    Returns:
        格式化后的行字符串。
    """
    # 截断过长字段以适应列宽
    sid_str = sid[:id_width].ljust(id_width)
    title_str = title[:title_width].ljust(title_width)
    state_str = state[:state_width].ljust(state_width)
    return f"{sid_str}  {title_str}  {state_str}  {created_at}"


def _print_events(
    events: list[session_engine.SessionEvent],
    *,
    indent: str = "  ",
) -> None:
    """格式化打印事件列表。

    Args:
        events: 事件列表。
        indent: 行首缩进字符串。
    """
    if not events:
        print(f"{indent}（暂无事件）")
        return
    for ev in events:
        payload_str = ""
        if ev.payload:
            parts = [f"{k}={v}" for k, v in ev.payload.items()]
            payload_str = "  {" + ", ".join(parts) + "}"
        print(
            f"{indent}[{ev.seq:>4}] {ev.ts}  {ev.surface}/{ev.actor}"
            f"  {ev.type}{payload_str}"
        )


# ---------------------------------------------------------------------------
# Handler 函数
# ---------------------------------------------------------------------------


def handle_new(args: argparse.Namespace) -> int:
    """处理 ``world session new`` 命令。

    新建 session，取得写锁，向 stdout 输出 session_id，
    向 stderr 输出创建成功信息。

    Args:
        args: argparse 解析结果，含 ``title`` / ``task`` / ``lease`` 字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败。
    """
    state_dir = _find_state_dir()

    try:
        manifest = session_engine.create_session(
            state_dir,
            args.title,
            task_id=args.task or None,
            lease_minutes=args.lease,
        )
    except Exception as exc:
        print(f"错误：创建 session 失败：{exc}", file=sys.stderr)
        return 1

    # stdout 仅输出 session_id（便于脚本捕获）
    print(manifest.id)
    # stderr 输出人类可读信息
    print(
        f"[session] 创建成功：{manifest.id}  state={manifest.state}  "
        f"lease={args.lease}m",
        file=sys.stderr,
    )
    return 0


def handle_list(args: argparse.Namespace) -> int:
    """处理 ``world session list`` 命令。

    从 index.toml 加载全部 session 条目，以表格形式输出。

    Args:
        args: argparse 解析结果，含可选的 ``state`` 过滤字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败。
    """
    state_dir = _find_state_dir()

    try:
        entries = session_engine.load_index(state_dir)
    except Exception as exc:
        print(f"错误：加载索引失败：{exc}", file=sys.stderr)
        return 1

    # 按 state 过滤
    if args.state:
        entries = [e for e in entries if e.get("state") == args.state]

    if not entries:
        filter_hint = f"（state={args.state}）" if args.state else ""
        print(f"暂无 session{filter_hint}。")
        return 0

    # 表头
    id_w, title_w, state_w = 28, 28, 12
    header = _format_table_row(
        "ID",
        "TITLE",
        "STATE",
        "CREATED_AT",
        id_width=id_w,
        title_width=title_w,
        state_width=state_w,
    )
    print(header)
    print("-" * len(header))

    for entry in entries:
        print(
            _format_table_row(
                entry.get("id", ""),
                entry.get("title", ""),
                entry.get("state", ""),
                entry.get("created_at", ""),
                id_width=id_w,
                title_width=title_w,
                state_width=state_w,
            )
        )

    return 0


def handle_show(args: argparse.Namespace) -> int:
    """处理 ``world session show`` 命令。

    输出指定 session 的 manifest 摘要与最近 5 条事件。

    Args:
        args: argparse 解析结果，含 ``id`` 字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败（session 不存在等）。
    """
    state_dir = _find_state_dir()
    session_dir = state_dir / "sessions" / args.id

    if not session_dir.is_dir():
        print(
            f"错误 [WS001]：session 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1

    try:
        manifest = session_engine.load_manifest(session_dir)
    except session_engine.SessionNotFoundError:
        print(
            f"错误 [WS001]：session manifest 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"错误：加载 manifest 失败：{exc}", file=sys.stderr)
        return 1

    # 输出 manifest 摘要
    print("=" * 60)
    print(f"Session:   {manifest.id}")
    print(f"Title:     {manifest.title}")
    print(f"State:     {manifest.state}")
    print(f"Created:   {manifest.created_at}  by={manifest.created_by}")
    print(f"LastEvent: seq={manifest.last_event_seq}  writer={manifest.last_writer}")
    if manifest.task_id:
        print(f"Task:      {manifest.task_id}")
    if manifest.allowed_runtimes:
        print(f"Runtimes:  {', '.join(manifest.allowed_runtimes)}")

    # 锁状态
    lock = session_engine.load_lock(session_dir)
    if lock is not None:
        valid = session_engine.is_lock_valid(session_dir)
        lock_status = "有效" if valid else "已过期"
        print(
            f"Lock:      {lock_status}  holder={lock.surface}/{lock.instance_id}"
            f"  until={lock.lease_until}"
        )
    else:
        print("Lock:      无锁")

    # 最近 5 条事件
    print()
    print("最近 5 条事件：")
    try:
        recent_events = session_engine.read_events(session_dir, tail=5)
    except Exception as exc:
        print(f"  （读取事件失败：{exc}）")
        recent_events = []

    _print_events(recent_events)
    print("=" * 60)

    return 0


def handle_resume(args: argparse.Namespace) -> int:
    """处理 ``world session resume`` 命令。

    校验 session 存在且非 archived，尝试获取写锁，
    追加 ``session.resumed`` 事件，更新 manifest state 为 active。

    Args:
        args: argparse 解析结果，含 ``id`` / ``steal`` / ``lease`` 字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败。
    """
    state_dir = _find_state_dir()
    session_dir = state_dir / "sessions" / args.id

    if not session_dir.is_dir():
        print(
            f"错误 [WS001]：session 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1

    # 加载 manifest，检查是否 archived
    try:
        manifest = session_engine.load_manifest(session_dir)
    except session_engine.SessionNotFoundError:
        print(
            f"错误 [WS001]：session manifest 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1

    if manifest.state == "archived":
        print(
            f"错误 [WS002]：session '{args.id}' 已归档，无法 resume。",
            file=sys.stderr,
        )
        return 1

    # 尝试获取锁
    try:
        session_engine.acquire_lock(
            session_dir,
            surface="cli",
            actor="user",
            lease_minutes=args.lease,
            steal=args.steal,
        )
    except session_engine.LockHeldError as exc:
        print(f"错误 [WS101]：{exc}", file=sys.stderr)
        return 1
    except session_engine.SessionArchivedError as exc:
        print(f"错误 [WS002]：{exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"错误：获取锁失败：{exc}", file=sys.stderr)
        return 1

    # 追加 session.resumed 事件
    next_seq = manifest.last_event_seq + 1
    event = session_engine.SessionEvent(
        seq=next_seq,
        ts=_now_iso(),
        surface="cli",
        actor="user",
        type="session.resumed",
        payload={"lease_minutes": args.lease, "steal": args.steal},
    )
    try:
        session_engine.append_event(session_dir, event)
    except Exception as exc:
        print(f"错误：追加事件失败：{exc}", file=sys.stderr)
        return 1

    # 更新 manifest state 为 active
    updated = session_engine.SessionManifest(
        id=manifest.id,
        title=manifest.title,
        created_by=manifest.created_by,
        created_at=manifest.created_at,
        state="active",
        last_event_seq=next_seq,
        last_writer="cli",
        allowed_runtimes=manifest.allowed_runtimes,
        task_id=manifest.task_id,
    )
    session_engine.save_manifest(session_dir, updated)
    session_engine.update_index(state_dir, updated)

    print(
        f"[session] resume 成功：{args.id}  state=active  lease={args.lease}m",
        file=sys.stderr,
    )
    return 0


def handle_release(args: argparse.Namespace) -> int:
    """处理 ``world session release`` 命令。

    释放当前 session 的写锁，追加 ``lock.released`` 事件，
    更新 manifest state 为 suspended，更新 index。

    Args:
        args: argparse 解析结果，含可选的 ``id`` 字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败。
    """
    state_dir = _find_state_dir()

    # 确定 session_id：优先使用 --id，否则查找 active session
    session_id = getattr(args, "id", None)
    if not session_id:
        session_id = _find_active_session_id(state_dir)
        if session_id is None:
            print(
                "错误：未指定 --id 且当前无 active session。",
                file=sys.stderr,
            )
            return 1

    session_dir = state_dir / "sessions" / session_id

    if not session_dir.is_dir():
        print(
            f"错误 [WS001]：session 不存在：{session_id}",
            file=sys.stderr,
        )
        return 1

    try:
        manifest = session_engine.load_manifest(session_dir)
    except session_engine.SessionNotFoundError:
        print(
            f"错误 [WS001]：session manifest 不存在：{session_id}",
            file=sys.stderr,
        )
        return 1

    # 追加 lock.released 事件
    next_seq = manifest.last_event_seq + 1
    event = session_engine.SessionEvent(
        seq=next_seq,
        ts=_now_iso(),
        surface="cli",
        actor="user",
        type="lock.released",
        payload={},
    )
    try:
        session_engine.append_event(session_dir, event)
    except Exception as exc:
        print(f"错误：追加事件失败：{exc}", file=sys.stderr)
        return 1

    # 释放锁文件
    try:
        session_engine.release_lock(session_dir)
    except Exception as exc:
        print(f"错误：释放锁失败：{exc}", file=sys.stderr)
        return 1

    # 更新 manifest state 为 suspended
    updated = session_engine.SessionManifest(
        id=manifest.id,
        title=manifest.title,
        created_by=manifest.created_by,
        created_at=manifest.created_at,
        state="suspended",
        last_event_seq=next_seq,
        last_writer="cli",
        allowed_runtimes=manifest.allowed_runtimes,
        task_id=manifest.task_id,
    )
    session_engine.save_manifest(session_dir, updated)
    session_engine.update_index(state_dir, updated)

    print(
        f"[session] release 成功：{session_id}  state=suspended",
        file=sys.stderr,
    )
    return 0


def handle_archive(args: argparse.Namespace) -> int:
    """处理 ``world session archive`` 命令。

    校验 session 锁已释放（非 active），追加 ``session.archived`` 事件，
    更新 manifest state 为 archived，更新 index。
    不做物理目录迁移，仅更新状态。

    Args:
        args: argparse 解析结果，含 ``id`` 字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败。
    """
    state_dir = _find_state_dir()
    session_dir = state_dir / "sessions" / args.id

    if not session_dir.is_dir():
        print(
            f"错误 [WS001]：session 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1

    try:
        manifest = session_engine.load_manifest(session_dir)
    except session_engine.SessionNotFoundError:
        print(
            f"错误 [WS001]：session manifest 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1

    if manifest.state == "archived":
        print(
            f"[session] session '{args.id}' 已处于 archived 状态，无需重复归档。",
            file=sys.stderr,
        )
        return 0

    # 检查锁是否仍被持有（state=active 且锁有效）
    if manifest.state == "active" and session_engine.is_lock_valid(session_dir):
        print(
            f"错误：session '{args.id}' 当前处于 active 状态且锁有效，"
            "请先执行 `world session release` 释放锁后再归档。",
            file=sys.stderr,
        )
        return 1

    # 追加 session.archived 事件
    next_seq = manifest.last_event_seq + 1
    event = session_engine.SessionEvent(
        seq=next_seq,
        ts=_now_iso(),
        surface="cli",
        actor="user",
        type="session.archived",
        payload={"title": manifest.title},
    )
    try:
        session_engine.append_event(session_dir, event)
    except Exception as exc:
        print(f"错误：追加事件失败：{exc}", file=sys.stderr)
        return 1

    # 更新 manifest state 为 archived
    updated = session_engine.SessionManifest(
        id=manifest.id,
        title=manifest.title,
        created_by=manifest.created_by,
        created_at=manifest.created_at,
        state="archived",
        last_event_seq=next_seq,
        last_writer="cli",
        allowed_runtimes=manifest.allowed_runtimes,
        task_id=manifest.task_id,
    )
    session_engine.save_manifest(session_dir, updated)
    session_engine.update_index(state_dir, updated)

    print(
        f"[session] archive 成功：{args.id}  state=archived",
        file=sys.stderr,
    )
    return 0


def handle_log(args: argparse.Namespace) -> int:
    """处理 ``world session log`` 命令。

    读取指定 session 的事件流并格式化输出。

    Args:
        args: argparse 解析结果，含 ``id`` 与可选的 ``tail`` 字段。

    Returns:
        退出码：``0`` 成功，``1`` 失败。
    """
    state_dir = _find_state_dir()
    session_dir = state_dir / "sessions" / args.id

    if not session_dir.is_dir():
        print(
            f"错误 [WS001]：session 不存在：{args.id}",
            file=sys.stderr,
        )
        return 1

    try:
        events = session_engine.read_events(session_dir, tail=args.tail)
    except Exception as exc:
        print(f"错误：读取事件失败：{exc}", file=sys.stderr)
        return 1

    tail_hint = f"（最近 {args.tail} 条）" if args.tail else f"（共 {len(events)} 条）"
    print(f"Session {args.id} 事件日志 {tail_hint}：")
    _print_events(events, indent="  ")

    return 0


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """返回当前时间的 ISO 8601 with offset 字符串。

    Returns:
        当前时间的 ISO 8601 字符串（含时区偏移）。
    """
    from datetime import datetime

    return datetime.now(UTC).astimezone().isoformat()


def _find_active_session_id(state_dir: Path) -> str | None:
    """从 index.toml 中查找第一个 state=active 的 session_id。

    Args:
        state_dir: ``world.state/`` 目录路径。

    Returns:
        找到时返回 session_id 字符串，否则返回 ``None``。
    """
    try:
        entries = session_engine.load_index(state_dir)
    except Exception:
        return None
    for entry in entries:
        if entry.get("state") == "active":
            return entry.get("id")
    return None


# ---------------------------------------------------------------------------
# 注册函数
# ---------------------------------------------------------------------------


def register_session_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """注册 ``session`` 子命令组到 world CLI。

    在给定的 subparsers 上注册 ``session`` 命令，并在其下嵌套
    new / list / show / resume / release / archive / log 七个二级子命令。

    Args:
        subparsers: argparse 的子命令注册器，由父 parser 的
            ``add_subparsers()`` 返回。
    """
    session_parser: argparse.ArgumentParser = subparsers.add_parser(
        "session",
        help="管理 World Session 生命周期",
        description=(
            "world session 子命令族：创建、列出、查看、恢复、释放、归档、"
            "查看日志等操作。所有操作基于 .agents/world.state/ 目录。"
        ),
    )

    session_sub = session_parser.add_subparsers(
        dest="session_cmd",
        metavar="<subcommand>",
    )

    # ------------------------------------------------------------------
    # world session new <title>
    # ------------------------------------------------------------------
    new_parser = session_sub.add_parser(
        "new",
        help="新建 session 并取得写锁",
        description="新建 session，生成 session_id，创建目录骨架，写入初始事件。",
    )
    new_parser.add_argument(
        "title",
        metavar="TITLE",
        help="会话标题（自由文本）",
    )
    new_parser.add_argument(
        "--task",
        default=None,
        metavar="TASK_ID",
        help="关联的长任务 ID（可选）",
    )
    new_parser.add_argument(
        "--lease",
        type=int,
        default=10,
        metavar="MINUTES",
        help="锁租约时长（分钟），默认 10",
    )
    new_parser.set_defaults(handler=handle_new)

    # ------------------------------------------------------------------
    # world session list [--state STATE]
    # ------------------------------------------------------------------
    list_parser = session_sub.add_parser(
        "list",
        help="列出全部 session（可按 state 过滤）",
        description="从 index.toml 加载全部 session 索引条目，以表格形式输出。",
    )
    list_parser.add_argument(
        "--state",
        default=None,
        choices=["active", "suspended", "archived"],
        metavar="STATE",
        help="按状态过滤（active / suspended / archived）",
    )
    list_parser.set_defaults(handler=handle_list)

    # ------------------------------------------------------------------
    # world session show <id>
    # ------------------------------------------------------------------
    show_parser = session_sub.add_parser(
        "show",
        help="查看 session 详情（manifest + 最近 5 条事件）",
        description="输出指定 session 的 manifest 摘要与最近 5 条事件。",
    )
    show_parser.add_argument(
        "id",
        metavar="SESSION_ID",
        help="目标 session_id",
    )
    show_parser.set_defaults(handler=handle_show)

    # ------------------------------------------------------------------
    # world session resume <id>
    # ------------------------------------------------------------------
    resume_parser = session_sub.add_parser(
        "resume",
        help="恢复 session：取锁并设为 active",
        description=(
            "校验 session 存在且非 archived，尝试获取写锁，"
            "追加 session.resumed 事件，更新 state 为 active。"
        ),
    )
    resume_parser.add_argument(
        "id",
        metavar="SESSION_ID",
        help="目标 session_id",
    )
    resume_parser.add_argument(
        "--steal",
        action="store_true",
        default=False,
        help="强制夺锁（仅当锁已过期时有效）",
    )
    resume_parser.add_argument(
        "--lease",
        type=int,
        default=10,
        metavar="MINUTES",
        help="锁租约时长（分钟），默认 10",
    )
    resume_parser.set_defaults(handler=handle_resume)

    # ------------------------------------------------------------------
    # world session release [--id SESSION_ID]
    # ------------------------------------------------------------------
    release_parser = session_sub.add_parser(
        "release",
        help="释放写锁，session 进入 suspended 状态",
        description=(
            "释放当前 active session 的写锁，追加 lock.released 事件，"
            "更新 state 为 suspended。若未指定 --id 则自动查找当前 active session。"
        ),
    )
    release_parser.add_argument(
        "--id",
        default=None,
        metavar="SESSION_ID",
        dest="id",
        help="目标 session_id（缺省时自动查找 active session）",
    )
    release_parser.set_defaults(handler=handle_release)

    # ------------------------------------------------------------------
    # world session archive <id>
    # ------------------------------------------------------------------
    archive_parser = session_sub.add_parser(
        "archive",
        help="归档 session（state → archived）",
        description=(
            "校验 session 锁已释放后，追加 session.archived 事件，"
            "更新 state 为 archived。不做物理目录迁移，仅更新状态。"
        ),
    )
    archive_parser.add_argument(
        "id",
        metavar="SESSION_ID",
        help="目标 session_id",
    )
    archive_parser.set_defaults(handler=handle_archive)

    # ------------------------------------------------------------------
    # world session log <id> [--tail N]
    # ------------------------------------------------------------------
    log_parser = session_sub.add_parser(
        "log",
        help="查看 session 事件日志",
        description="读取并格式化输出指定 session 的 events.toml 内容。",
    )
    log_parser.add_argument(
        "id",
        metavar="SESSION_ID",
        help="目标 session_id",
    )
    log_parser.add_argument(
        "--tail",
        type=int,
        default=None,
        metavar="N",
        help="仅显示最近 N 条事件",
    )
    log_parser.set_defaults(handler=handle_log)

    # 若仅执行 `world session` 而无子命令，打印帮助
    session_parser.set_defaults(handler=_handle_session_help(session_parser))


def _handle_session_help(
    parser: argparse.ArgumentParser,
):
    """返回一个在未指定子命令时打印帮助的 handler。

    Args:
        parser: session 子命令的 ArgumentParser 实例。

    Returns:
        handler 函数，接受 args 并打印帮助后返回 0。
    """

    def _handler(args: argparse.Namespace) -> int:
        parser.print_help()
        return 0

    return _handler
