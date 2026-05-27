"""``world remove`` 子命令 — 卸载已安装的 Fragment。"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

from .._world_engines.manifest_parser import find_world_toml, parse_world_toml
from .._world_engines.world_updater import unregister_fragment


def register_remove_parser(subparsers: argparse._SubParsersAction) -> None:
    """注册 remove 子命令到 argparse。"""
    parser = subparsers.add_parser("remove", help="卸载已安装的 Fragment")
    parser.add_argument("name", help="要卸载的组件名")
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="跳过依赖者检查",
    )
    parser.add_argument(
        "--keep-files",
        action="store_true",
        default=False,
        help="仅注销，保留文件",
    )
    parser.set_defaults(handler=handle_remove)


def handle_remove(args: argparse.Namespace) -> int:
    """world remove 命令处理函数。"""
    # 1. 定位 world.toml
    world_toml_path = find_world_toml()
    if not world_toml_path:
        print("错误: 未找到 world.toml", file=sys.stderr)
        return 1

    # 2. 确认目标已注册
    world_info = parse_world_toml(world_toml_path)
    target = None
    for f in world_info.fragments:
        if f.name == args.name:
            target = f
            break
    if target is None:
        print(f"错误: Fragment '{args.name}' 未安装", file=sys.stderr)
        return 1

    # 3. 依赖者检查（除非 --force）
    if not args.force:
        dependents = _find_dependents(args.name, world_toml_path)
        if dependents:
            names = ", ".join(dependents)
            print(
                f"错误: 以下 Fragment 引用了 '{args.name}': {names}",
                file=sys.stderr,
            )
            print("使用 --force 跳过依赖者检查", file=sys.stderr)
            return 2

    # 4. 文件删除（除非 --keep-files）
    if not args.keep_files:
        _remove_fragment_files(args.name, world_toml_path)

    # 5. world.toml 注销
    unregister_fragment(args.name, world_toml_path)

    # 6. 输出成功信息
    print(f"已卸载: {args.name}")
    return 0


def _find_dependents(name: str, world_toml_path: Path) -> list[str]:
    """扫描 world.toml 查找引用目标 Fragment 的其他段。

    采用最简文本匹配策略：在每个非目标 fragment 段的文本范围内
    搜索目标名称的出现。

    Args:
        name: 待检查的目标 Fragment 名称。
        world_toml_path: world.toml 文件路径。

    Returns:
        引用了目标名称的其他 Fragment 名称列表。
    """
    text = world_toml_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    dependents: list[str] = []
    current_fragment: str | None = None
    section_re = re.compile(r"^\s*\[fragments\.([^\]]+)\]\s*$")
    any_section_re = re.compile(r"^\s*\[[^\]]+\]\s*$")

    for line in lines:
        section_match = section_re.match(line)
        if section_match:
            current_fragment = section_match.group(1).strip()
            continue
        if any_section_re.match(line):
            current_fragment = None
            continue
        # 在非目标 fragment 段中搜索目标名称
        if current_fragment and current_fragment != name:
            if name in line:
                if current_fragment not in dependents:
                    dependents.append(current_fragment)

    return dependents


def _remove_fragment_files(name: str, world_toml_path: Path) -> None:
    """删除 Fragment 对应的实际文件。

    从 world.toml 中读取该 fragment 的 includes 或 contents 列表，
    逐一删除 .agents/ 目录下的对应文件。

    Args:
        name: Fragment 名称。
        world_toml_path: world.toml 文件路径。
    """
    agents_dir = world_toml_path.parent

    # 读取原始 TOML 获取文件列表
    with world_toml_path.open("rb") as f:
        data = tomllib.load(f)

    fragments_data = data.get("fragments", {})
    frag_info = fragments_data.get(name, {})

    # 兼容两种字段名：includes（手写 world.toml）和 contents（程序注册）
    file_list = frag_info.get("includes") or frag_info.get("contents") or []

    if not file_list:
        print(
            f"警告: Fragment '{name}' 无文件清单，跳过文件删除",
            file=sys.stderr,
        )
        return

    removed = 0
    for rel_path in file_list:
        target_file = agents_dir / rel_path
        if target_file.exists():
            try:
                target_file.unlink()
                removed += 1
            except OSError as exc:
                print(f"警告: 无法删除 {rel_path}: {exc}", file=sys.stderr)
        else:
            print(f"跳过: {rel_path} (文件不存在)")

    if removed:
        print(f"已删除 {removed} 个文件")
