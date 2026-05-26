"""``world resolve`` 子命令 — 解析依赖图并生成 world.lock。"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from taolib.cli._world_engines.lock_generator import (
    LockFile,
    LockPackage,
    compute_world_toml_hash,
    generate_lock,
    parse_lock,
)
from taolib.cli._world_engines.manifest_parser import find_world_toml, parse_world_toml
from taolib.cli._world_engines.registry_config import load_registry_config
from taolib.cli._world_engines.registry_index import (
    query_entry,
    resolve_index_path,
    select_version,
)


def register_resolve_parser(
    subparsers: argparse._SubParsersAction,  # type: ignore[type-arg]
) -> None:
    """注册 ``resolve`` 子命令到 argparse。

    Args:
        subparsers: argparse 的子命令注册器，由父 parser 的
            ``add_subparsers()`` 返回。
    """
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "resolve",
        help="解析依赖并生成 world.lock",
        description="解析 world.toml 中的 fragments 依赖图，生成锁定文件 world.lock。",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="强制更新 Registry 缓存（忽略 TTL）",
    )
    parser.add_argument(
        "--locked",
        action="store_true",
        default=False,
        help="严格模式：要求 world.lock 与 world.toml 一致",
    )
    parser.set_defaults(handler=handle_resolve)


def handle_resolve(args: argparse.Namespace) -> int:
    """执行 ``world resolve`` 命令逻辑。

    流程：

    1. 定位 world.toml 并解析。
    2. 计算 world.toml 哈希。
    3. ``--locked`` 模式下校验 world.lock 一致性。
    4. 正常模式下遍历 fragments → 查询 Registry → 生成 world.lock。

    Args:
        args: 已解析的命令行参数。

    Returns:
        退出码：``0`` 成功，``1`` 一般错误，``10`` 解析失败。
    """
    # 1. 定位 world.toml
    world_toml_path = find_world_toml()
    if world_toml_path is None:
        print(
            "错误: 未找到 world.toml，请确认位于 AgentForge 世界目录",
            file=sys.stderr,
        )
        return 1

    # 2. 解析 world.toml
    try:
        world_info = parse_world_toml(world_toml_path)
    except Exception as exc:
        print(f"错误: 解析 world.toml 失败: {exc}", file=sys.stderr)
        return 1

    agents_dir = world_toml_path.parent

    # 3. 计算 world.toml 哈希
    current_hash = compute_world_toml_hash(world_toml_path)

    # 4. --locked 模式
    if args.locked:
        return _handle_locked_mode(agents_dir, current_hash)

    # 5. 正常解析模式
    return _handle_resolve_mode(args, world_info, agents_dir, current_hash)


def _handle_locked_mode(agents_dir: Path, current_hash: str) -> int:
    """处理 ``--locked`` 严格校验模式。

    Args:
        agents_dir: ``.agents/`` 目录路径。
        current_hash: 当前 world.toml 的 SHA256 哈希。

    Returns:
        退出码：``0`` 一致，``10`` 不一致或锁定文件缺失。
    """
    lock_path = agents_dir / "world.lock"
    lock_file = parse_lock(lock_path)

    if lock_file is None:
        print(
            "错误: world.lock 不存在或格式错误，请先运行 world resolve",
            file=sys.stderr,
        )
        return 10

    if lock_file.world_toml_hash != current_hash:
        print(
            "错误: world.toml 已变更，请重新解析 (world resolve)",
            file=sys.stderr,
        )
        return 10

    print("world.lock 已锁定且一致")
    return 0


def _handle_resolve_mode(
    args: argparse.Namespace,
    world_info: object,
    agents_dir: Path,
    current_hash: str,
) -> int:
    """处理正常依赖解析模式。

    Args:
        args: 命令行参数（含 ``--update``）。
        world_info: 解析后的 :class:`~taolib.cli._world_engines.manifest_parser.WorldInfo`。
        agents_dir: ``.agents/`` 目录路径。
        current_hash: 当前 world.toml 的 SHA256 哈希。

    Returns:
        退出码：``0`` 成功，``1`` 一般错误，``10`` 解析失败。
    """
    # 加载 Registry 配置
    registry_sources = load_registry_config(agents_dir)
    if not registry_sources:
        print(
            "错误: 未配置 Registry 源（.agents/registry.toml）",
            file=sys.stderr,
        )
        return 1

    packages: list[LockPackage] = []

    for frag in world_info.fragments:  # type: ignore[attr-defined]
        resolved = _resolve_fragment(frag, registry_sources, args.update)
        if resolved is None:
            print(
                f"错误: 在 Registry 中未找到 '{frag.name}' 的匹配版本"
                f" (约束: {frag.version or 'latest.stable'})",
                file=sys.stderr,
            )
            return 10
        packages.append(resolved)

    # 构建 LockFile
    now_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lock_file = LockFile(
        generated=now_utc,
        resolver_version="1",
        world_toml_hash=current_hash,
        packages=packages,
    )

    # 写入 world.lock
    lock_path = agents_dir / "world.lock"
    generate_lock(lock_file, lock_path)

    # 打印成功摘要
    print(f"已解析 {len(packages)} 个依赖包，写入 {lock_path.name}")
    for pkg in packages:
        print(f"  {pkg.name}@{pkg.version} ({pkg.source})")

    return 0


def _resolve_fragment(
    frag: object,
    registry_sources: list,
    force_update: bool,
) -> LockPackage | None:
    """解析单个 Fragment 的 Registry 引用。

    Args:
        frag: :class:`~taolib.cli._world_engines.manifest_parser.InstalledFragment`
            实例。
        registry_sources: 按优先级排列的 Registry 源列表。
        force_update: 是否强制更新缓存。

    Returns:
        构建好的 :class:`LockPackage`，未找到匹配时返回 ``None``。
    """
    constraint = frag.version if frag.version else None  # type: ignore[attr-defined]

    for source in registry_sources:
        index_path = resolve_index_path(source, force_update=force_update)
        if index_path is None:
            continue

        entry = query_entry(index_path, frag.name)  # type: ignore[attr-defined]
        if entry is None:
            continue

        version = select_version(entry, constraint)
        if version is None:
            continue

        return LockPackage(
            name=frag.name,  # type: ignore[attr-defined]
            version=version.version,
            type=entry.entry_type,
            source=f"registry+{source.name}",
            git_url=version.git_url,
            git_ref=version.git_ref,
            checksum=version.checksum,
            dependencies=[],
        )

    return None
