"""``world route`` 子命令：解析路由查询并输出匹配 targets。

根据 ``routing-protocol.md`` Draft v0.1 描述的声明式上下文路由协议，
本子命令接收 ``--intent`` / ``--file`` / ``--phase`` / ``--role`` 等查询
维度，调用 :mod:`taolib.cli._world_engines.routing_engine` 评估匹配规则，
并以 JSON 或纯路径列表的形式输出 ``resolved_targets``。

示例::

    $ world route --intent python --file pyproject.toml --phase coding
    {
      "routing_version": "0.1.0",
      ...
    }
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

from taolib.cli._world_engines import routing_engine


def _find_world_toml() -> Path | None:
    """从当前目录向上逐级查找 ``.agents/world.toml``。

    Returns:
        找到时返回 ``world.toml`` 的绝对路径，否则返回 ``None``。
    """
    current = Path.cwd().resolve()
    for directory in [current, *current.parents]:
        candidate = directory / ".agents" / "world.toml"
        if candidate.is_file():
            return candidate
    return None


def register_route_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """注册 ``route`` 子命令到给定的 subparsers。

    Args:
        subparsers: argparse 的子命令注册器，由父 parser 的
            ``add_subparsers()`` 返回。
    """
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "route",
        help="按 intent/file/phase/role 维度解析路由匹配",
        description=(
            "解析当前 .agents/world.toml 的 [routing] 配置，根据查询维度"
            "评估匹配规则并输出 targets 资产路径。"
        ),
    )
    parser.add_argument(
        "--intent",
        action="append",
        default=[],
        metavar="TEXT",
        help="任务意图关键词（可多次指定）",
    )
    parser.add_argument(
        "--file",
        action="append",
        default=[],
        metavar="PATH",
        help="涉及的文件路径（可多次指定）",
    )
    parser.add_argument(
        "--phase",
        default=None,
        metavar="TEXT",
        help="当前 session 阶段",
    )
    parser.add_argument(
        "--role",
        default=None,
        metavar="TEXT",
        help="当前 agent 角色 id",
    )
    parser.add_argument(
        "--strategy",
        default=None,
        choices=["merge", "priority-first"],
        help="冲突解决策略覆盖（默认使用 world.toml 中配置）",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="在 stderr 输出详细匹配过程信息",
    )
    parser.add_argument(
        "--targets-only",
        action="store_true",
        help="仅输出 targets 路径列表（非 JSON），每行一条",
    )
    parser.add_argument(
        "--include-bindings",
        action="store_true",
        help="包含 Role Default Bindings 并合并到 all_targets",
    )
    parser.set_defaults(handler=handle_route)


def _log_verbose(
    enabled: bool,
    config: routing_engine.RoutingConfig,
    matches: list[routing_engine.RouteMatch],
    strategy: str,
) -> None:
    """在 stderr 打印详细匹配过程信息。

    Args:
        enabled: 是否启用 verbose 输出。
        config: 已解析的路由配置。
        matches: 匹配规则列表。
        strategy: 实际使用的冲突解决策略。
    """
    if not enabled:
        return
    print(
        f"[route] routing_version={config.version} "
        f"strategy={strategy} rules={len(config.rules)} matches={len(matches)}",
        file=sys.stderr,
    )
    for m in matches:
        print(
            f"[route] match rule_id={m.rule_id} priority={m.priority} "
            f"matched_by={','.join(m.matched_by)} targets={len(m.targets)}",
            file=sys.stderr,
        )


def handle_route(args: argparse.Namespace) -> int:
    """执行 ``world route`` 命令逻辑。

    Args:
        args: 由 argparse 解析的命名空间。

    Returns:
        退出码：``0`` 表示成功，``1`` 表示定位或解析失败。
    """
    toml_path = _find_world_toml()
    if toml_path is None:
        print(
            "错误：在当前目录及其所有父目录中均未找到 .agents/world.toml",
            file=sys.stderr,
        )
        return 1

    try:
        config = routing_engine.parse_routing_config(toml_path)
    except FileNotFoundError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except KeyError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except tomllib.TOMLDecodeError as exc:
        print(f"错误：解析 {toml_path} 失败：{exc}", file=sys.stderr)
        return 1

    strategy = args.strategy or config.conflict_resolution

    try:
        matches = routing_engine.resolve_routes(
            config,
            intents=list(args.intent),
            files=list(args.file),
            phase=args.phase,
            role=args.role,
        )
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    _log_verbose(args.verbose, config, matches, strategy)

    try:
        resolved_targets = routing_engine.collect_targets(matches, strategy)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    role_bindings: list[str] | None = None
    all_targets: list[str] | None = None
    if args.include_bindings and args.role:
        roles_dir = toml_path.parent / "roles"
        role_bindings = routing_engine.resolve_role_bindings(roles_dir, args.role)
        seen: set[str] = set()
        all_targets = []
        for item in [*resolved_targets, *role_bindings]:
            if item not in seen:
                seen.add(item)
                all_targets.append(item)

    if args.targets_only:
        for path in all_targets if all_targets is not None else resolved_targets:
            print(path)
        return 0

    payload: dict[str, object] = {
        "routing_version": config.version,
        "query": {
            "intents": list(args.intent),
            "files": list(args.file),
            "phase": args.phase,
            "role": args.role,
        },
        "strategy": strategy,
        "matches": [
            {
                "rule_id": m.rule_id,
                "targets": list(m.targets),
                "priority": m.priority,
                "matched_by": list(m.matched_by),
            }
            for m in matches
        ],
        "resolved_targets": resolved_targets,
    }
    if role_bindings is not None and all_targets is not None:
        payload["role_bindings"] = role_bindings
        payload["all_targets"] = all_targets

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0
