"""``world status`` 子命令：显示当前世界配置状态。

从当前工作目录向上逐级查找 ``.agents/world.toml``，解析后
以人类可读格式输出世界名称、版本、fragment 列表与 capabilities。
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path


def _find_world_toml() -> Path | None:
    """从当前目录向上逐级查找 ``.agents/world.toml``。

    遵循多世界层级继承的"最近原则"：返回距当前目录最近的一个。

    Returns:
        找到时返回 ``world.toml`` 的绝对路径，否则返回 ``None``。
    """
    current = Path.cwd().resolve()
    for directory in [current, *current.parents]:
        candidate = directory / ".agents" / "world.toml"
        if candidate.is_file():
            return candidate
    return None


def _format_status(data: dict) -> str:  # type: ignore[type-arg]
    """将解析后的 world.toml 数据格式化为可读字符串。

    Args:
        data: 由 ``tomllib.load`` 解析得到的 TOML 字典。

    Returns:
        格式化后的多行字符串。
    """
    lines: list[str] = []

    world = data.get("world", {})
    name = world.get("name", "(unknown)")
    version = world.get("version", "(unknown)")
    lines.append(f"World: {name} (Kernel {version})")

    fragments: dict = data.get("fragments", {})
    capabilities: dict = data.get("capabilities", {})

    # 统计 capabilities 中的非嵌套字符串型条目数量
    cap_items = {k: v for k, v in capabilities.items() if isinstance(v, str)}
    lines.append(
        f"Installed: {len(fragments)} fragments, {len(cap_items)} capabilities"
    )

    if fragments:
        lines.append("")
        lines.append("FRAGMENTS")
        for frag_name, frag_data in fragments.items():
            frag_version = frag_data.get("version", "(unknown)")
            optional = frag_data.get("optional", False)
            optional_tag = "  (optional)" if optional else ""
            lines.append(f"  {frag_name:<28}{frag_version}{optional_tag}")

    if cap_items:
        lines.append("")
        lines.append("CAPABILITIES")
        for cap_key, _cap_val in cap_items.items():
            lines.append(f"  {cap_key + '/':<14}directory")

    return "\n".join(lines)


def register_status_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """注册 ``status`` 子命令到给定的 subparsers。

    Args:
        subparsers: argparse 的子命令注册器，由父 parser 的
            ``add_subparsers()`` 返回。
    """
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "status",
        help="显示当前世界配置状态",
        description="从当前目录向上查找 .agents/world.toml 并输出世界状态摘要。",
    )
    parser.set_defaults(handler=handle_status)


def handle_status(args: argparse.Namespace) -> int:
    """执行 ``world status`` 命令逻辑。

    Args:
        args: 由 argparse 解析的命名空间（当前未使用额外参数）。

    Returns:
        退出码：``0`` 表示成功，``1`` 表示未找到 world.toml 或解析失败。
    """
    toml_path = _find_world_toml()
    if toml_path is None:
        print(
            "错误：在当前目录及其所有父目录中均未找到 .agents/world.toml",
            file=sys.stderr,
        )
        return 1

    try:
        with toml_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        print(f"错误：解析 {toml_path} 失败：{exc}", file=sys.stderr)
        return 1

    print(_format_status(data))
    return 0
