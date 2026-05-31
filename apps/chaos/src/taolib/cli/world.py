"""``world`` 命令行入口。

本模块提供 World CLI 的主入口，当前支持以下子命令：

- ``init``：生成 AGENTS.md + .agents/ 项目骨架（新项目零配置启动）。
- ``guide``：项目结构诊断与 Fragment 推荐（打破 init 后的静默期）。
- ``status``：显示当前世界配置状态，解析 ``.agents/world.toml``。
- ``install``：安装世界 fragment（``--dry-run`` 模式）。
- ``resolve``：解析世界 fragment 依赖与版本约束。
- ``remove``：移除已安装的世界 fragment。
- ``publish``：发布世界 fragment 至 registry。
- ``session``：管理 World Session 生命周期。

示例::

    $ world init --name my-project
    $ world status
    World: my-project (Kernel 0.1.0)
    Installed: 7 fragments, 2 capabilities
    ...
"""

from __future__ import annotations

import argparse
import sys

from taolib.cli._world_commands.fragment_init import register_fragment_init_parser
from taolib.cli._world_commands.guide import register_guide_parser
from taolib.cli._world_commands.init import register_init_parser
from taolib.cli._world_commands.install import register_install_parser
from taolib.cli._world_commands.publish import register_publish_parser
from taolib.cli._world_commands.remove import register_remove_parser
from taolib.cli._world_commands.resolve import register_resolve_parser
from taolib.cli._world_commands.route import register_route_parser
from taolib.cli._world_commands.session import register_session_parser
from taolib.cli._world_commands.status import register_status_parser


def build_parser() -> argparse.ArgumentParser:
    """构建 ``world`` 命令的 argparse 解析器。

    Returns:
        配置好所有子命令的 :class:`argparse.ArgumentParser` 实例。
    """
    parser = argparse.ArgumentParser(
        prog="world",
        description="World CLI - 世界分发管理工具",
    )
    subparsers = parser.add_subparsers(dest="command")

    register_init_parser(subparsers)
    register_guide_parser(subparsers)
    register_status_parser(subparsers)

    # Fragment 子命令组
    fragment_parser = subparsers.add_parser(
        "fragment",
        help="Fragment 管理（创建、安装、移除、发布）",
        description="管理 AgentForge Fragments——创建新 Fragment、从规则打包、安装、移除、发布。",
    )
    fragment_subparsers = fragment_parser.add_subparsers(dest="fragment_command")
    register_fragment_init_parser(fragment_subparsers)
    register_install_parser(fragment_subparsers)
    register_remove_parser(fragment_subparsers)
    register_publish_parser(fragment_subparsers)
    register_resolve_parser(fragment_subparsers)

    # 其他顶层命令（兼容旧用法，直接 world install/remove 等也可用）
    register_install_parser(subparsers)
    register_resolve_parser(subparsers)
    register_remove_parser(subparsers)
    register_publish_parser(subparsers)
    register_route_parser(subparsers)
    register_session_parser(subparsers)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 主入口。

    Args:
        argv: 可选参数列表，为 ``None`` 时默认使用 :data:`sys.argv`。

    Returns:
        进程退出码：``0`` 表示成功，非零表示错误。
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    handler = getattr(args, "handler", None)
    if handler is not None:
        return handler(args)

    print(f"子命令 '{args.command}' 尚未实现。", file=sys.stderr)
    return 1


__all__ = ["main", "build_parser"]

if __name__ == "__main__":
    raise SystemExit(main())
