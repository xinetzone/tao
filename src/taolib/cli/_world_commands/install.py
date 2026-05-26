from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .._world_engines.compat_engine import ValidationLevel, validate
from .._world_engines.fetcher import FetchError, FetchResult, fetch_git
from .._world_engines.file_manager import (
    PlaceContext,
    PlaceError,
    place_fragment,
    rollback,
)
from .._world_engines.hooks_engine import execute_lifecycle_hooks
from .._world_engines.manifest_parser import (
    FragmentManifest,
    WorldInfo,
    find_world_toml,
    parse_manifest,
    parse_world_toml,
)
from .._world_engines.registry_config import load_registry_config
from .._world_engines.registry_index import (
    query_entry,
    resolve_index_path,
    select_version,
)
from .._world_engines.source_parser import ParsedSource, SourceType, parse_source
from .._world_engines.world_updater import register_fragment, unregister_fragment

_LEVEL_LABELS = {
    ValidationLevel.L1_KERNEL_COMPAT: "L1 Kernel compat",
    ValidationLevel.L2_CONFLICTS: "L2 Conflicts",
    ValidationLevel.L3_DEPENDENCIES: "L3 Dependencies",
    ValidationLevel.L4_FILE_CONFLICTS: "L4 File conflicts",
}


def _is_local_source(source: str) -> bool:
    """判断 source 是否为本地路径（保留向后兼容的工具函数）。

    Args:
        source: 命令行传入的 source 字符串。

    Returns:
        若为本地路径则返回 ``True``。
    """
    return source.startswith(("./", "/", "\\")) or Path(source).exists()


def _level_pass_detail(
    level: ValidationLevel,
    manifest: FragmentManifest,
    world: WorldInfo,
) -> str:
    """生成某层级 PASS 时的附加说明。"""
    if level == ValidationLevel.L1_KERNEL_COMPAT and manifest.kernel_compat:
        return (
            f" (requires >={manifest.kernel_compat.min_version},"
            f" <{manifest.kernel_compat.max_version};"
            f" current {world.version})"
        )
    if level == ValidationLevel.L2_CONFLICTS:
        return " (no conflicts)"
    if level == ValidationLevel.L3_DEPENDENCIES:
        return " (all satisfied)"
    if level == ValidationLevel.L4_FILE_CONFLICTS:
        return " (no conflicts)"
    return ""


def _print_dry_run_report(
    manifest: FragmentManifest,
    world: WorldInfo,
    source_path: Path,
    result: Any,
) -> None:
    """打印 ``--dry-run`` 模式的格式化报告。

    Args:
        manifest: 待安装 Fragment 的 manifest。
        world: 当前世界的 world.toml 解析结果。
        source_path: Fragment 的源目录路径。
        result: :class:`~taolib.cli._world_engines.compat_engine.ValidationResult`
            实例。
    """
    print(
        f"[dry-run] Installing {manifest.name}@{manifest.version}"
        f" from {source_path}"
    )
    print("\nCompatibility check:")

    errors_by_level = {level: [] for level in ValidationLevel}
    for err in result.errors:
        errors_by_level[err.level].append(err)

    previous_failed = False
    for level in ValidationLevel:
        level_errors = errors_by_level[level]
        label = _LEVEL_LABELS[level]

        if previous_failed:
            print(f"  {label + ':':<20} SKIP (blocked by previous failure)")
            continue

        if level_errors:
            print(f"  {label + ':':<20} FAIL")
            for err in level_errors:
                print(f"    - {err.message}")
            previous_failed = True
        else:
            detail = _level_pass_detail(level, manifest, world)
            print(f"  {label + ':':<20} PASS{detail}")

    if result.passed:
        print("\nWould install:")
        all_paths = (
            manifest.contents.rules
            + manifest.contents.skills
            + manifest.contents.scripts
            + manifest.contents.docs
            + manifest.contents.templates
        )
        for p in all_paths:
            print(f"  {p:<22} -> .agents/{p}")
        print("\nNo changes made (--dry-run).")
    else:
        print("\nInstallation blocked. Fix the above errors before installing.")


def register_install_parser(subparsers: Any) -> None:
    """注册 ``install`` 子命令及其参数。

    Args:
        subparsers: ``argparse.ArgumentParser.add_subparsers()`` 返回的
            subparsers 对象。
    """
    install_parser = subparsers.add_parser("install", help="安装世界 fragment")
    install_parser.set_defaults(handler=handle_install)
    install_parser.add_argument(
        "source",
        help="Fragment 源（本地路径 / Registry 引用 name[@constraint] / Git URL）",
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅模拟安装，不实际写入文件",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="强制覆盖已存在的目标文件",
    )
    install_parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="跳过生命周期钩子",
    )
    install_parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="强制更新 Registry 缓存（忽略 TTL）",
    )


def handle_install(args: argparse.Namespace) -> int:
    """执行 ``world install`` 命令逻辑。

    支持三种 source 类型：

    - :attr:`SourceType.LOCAL`：本地路径，直接读取 ``manifest.toml``。
    - :attr:`SourceType.REGISTRY`：``name[@constraint]`` 形式，
      通过 ``.agents/registry.toml`` 查表 → 选择版本 → Git fetch。
    - :attr:`SourceType.GIT_URL`：``https://`` / ``git@`` 形式，
      直接 Git fetch。

    所有路径最终复用同一套 validate → place → register → hooks 流程。

    Args:
        args: 已解析的命令行参数。

    Returns:
        进程退出码：``0`` 表示成功，``1`` 表示一般错误，
        ``2`` 表示校验失败或文件放置错误。
    """
    parsed = parse_source(args.source)

    match parsed.source_type:
        case SourceType.LOCAL:
            return _handle_local(parsed, args)
        case SourceType.REGISTRY:
            return _handle_registry(parsed, args)
        case SourceType.GIT_URL:
            return _handle_git_url(parsed, args)

    # 理论不可达：parse_source 仅返回上述三种 SourceType
    print(f"错误: 不支持的 source 类型: {parsed.source_type}", file=sys.stderr)
    return 1


def _handle_local(parsed: ParsedSource, args: argparse.Namespace) -> int:
    """处理本地路径 source（保持原型阶段行为不变）。"""
    source = parsed.raw
    source_path = Path(source)
    if not source_path.exists():
        print(f"Error: source path '{source}' does not exist", file=sys.stderr)
        return 1

    if source_path.is_dir():
        manifest_path = source_path / "manifest.toml"
    else:
        print(
            f"Error: source '{source}' is not a directory", file=sys.stderr
        )
        return 1

    if not manifest_path.exists():
        print(
            f"Error: manifest.toml not found in {source_path}",
            file=sys.stderr,
        )
        return 1

    return _install_from_resolved(
        manifest_path=manifest_path,
        source_path=source_path,
        args=args,
    )


def _handle_registry(parsed: ParsedSource, args: argparse.Namespace) -> int:
    """处理 Registry 引用 source（``name[@constraint]``）。"""
    if not parsed.name:
        print("错误: Registry 引用缺少组件名", file=sys.stderr)
        return 1

    world_toml_path = find_world_toml()
    if world_toml_path is None:
        print(
            "错误: 未找到 world.toml，请确认位于 AgentForge 世界目录",
            file=sys.stderr,
        )
        return 1
    agents_dir = world_toml_path.parent

    registry_sources = load_registry_config(agents_dir)
    if not registry_sources:
        print(
            "错误: 未配置 Registry 源（.agents/registry.toml）",
            file=sys.stderr,
        )
        return 1

    entry = None
    for source in registry_sources:
        index_path = resolve_index_path(source, force_update=args.update)
        if index_path is None:
            continue
        entry = query_entry(index_path, parsed.name)
        if entry is not None:
            break

    if entry is None:
        print(
            f"错误: 在 Registry 中未找到 '{parsed.name}'",
            file=sys.stderr,
        )
        return 1

    version = select_version(entry, parsed.constraint)
    if version is None:
        constraint_desc = parsed.constraint or "latest.stable"
        print(
            f"错误: '{parsed.name}' 无匹配版本 ({constraint_desc})",
            file=sys.stderr,
        )
        return 1

    try:
        fetch_result = fetch_git(
            version.git_url,
            version.git_ref,
            version.manifest_path,
        )
    except FetchError as exc:
        print(f"错误: 获取 Fragment 失败: {exc}", file=sys.stderr)
        return 1

    return _install_with_cleanup(fetch_result, args)


def _handle_git_url(parsed: ParsedSource, args: argparse.Namespace) -> int:
    """处理 Git URL 直接拉取 source。"""
    if not parsed.url:
        print("错误: Git URL 为空", file=sys.stderr)
        return 1

    try:
        fetch_result = fetch_git(parsed.url, parsed.ref or "HEAD")
    except FetchError as exc:
        print(f"错误: 获取 Fragment 失败: {exc}", file=sys.stderr)
        return 1

    return _install_with_cleanup(fetch_result, args)


def _install_with_cleanup(
    fetch_result: FetchResult,
    args: argparse.Namespace,
) -> int:
    """对已 fetch 到本地的 Fragment 执行通用安装流程，并保证临时目录回收。"""
    try:
        return _install_from_resolved(
            manifest_path=fetch_result.manifest_path,
            source_path=fetch_result.local_path,
            args=args,
        )
    finally:
        fetch_result.cleanup()


def _install_from_resolved(
    *,
    manifest_path: Path,
    source_path: Path,
    args: argparse.Namespace,
) -> int:
    """已解析到本地后的通用安装流程。

    流程：parse_manifest → parse_world_toml → validate →
    （--dry-run 输出报告 / 否则执行 place → register → hooks）。

    Args:
        manifest_path: Fragment 的 ``manifest.toml`` 完整路径。
        source_path: Fragment 源目录（manifest 所在目录或仓库根）。
        args: 命令行参数（透传 ``--dry-run`` / ``--force`` / ``--no-hooks``）。

    Returns:
        进程退出码：``0`` 成功；``1`` 一般错误；``2`` 校验失败或放置错误。
    """
    try:
        manifest = parse_manifest(manifest_path)
    except Exception as exc:
        print(f"Error: failed to parse manifest.toml: {exc}", file=sys.stderr)
        return 1

    world_toml_path = find_world_toml()
    if world_toml_path is None:
        print(
            "Error: world.toml not found. "
            "Are you in an AgentForge world directory?",
            file=sys.stderr,
        )
        return 1

    try:
        world_info = parse_world_toml(world_toml_path)
    except Exception as exc:
        print(f"Error: failed to parse world.toml: {exc}", file=sys.stderr)
        return 1

    agents_dir = world_toml_path.parent

    result = validate(manifest, world_info, agents_dir)

    # --force 模式允许覆盖 L4 文件冲突
    if args.force and not args.dry_run:
        filtered_errors = [
            err for err in result.errors
            if err.level != ValidationLevel.L4_FILE_CONFLICTS
        ]
        result.errors = filtered_errors
        result.passed = len(filtered_errors) == 0

    if args.dry_run:
        _print_dry_run_report(manifest, world_info, source_path, result)
        return 0 if result.passed else 2

    if not result.passed:
        _print_dry_run_report(manifest, world_info, source_path, result)
        return 2

    return _perform_install(
        manifest=manifest,
        source_path=source_path,
        agents_dir=agents_dir,
        world_toml_path=world_toml_path,
        force=args.force,
        no_hooks=args.no_hooks,
    )


def _perform_install(
    *,
    manifest: FragmentManifest,
    source_path: Path,
    agents_dir: Path,
    world_toml_path: Path,
    force: bool,
    no_hooks: bool,
) -> int:
    """实际执行 Fragment 安装的副本流程。

    在校验通过之后被调用，负责文件复制、world.toml 注册、生命周期钩子
    执行以及失败时的回滚。

    Args:
        manifest: 已解析的 Fragment manifest。
        source_path: Fragment 源目录。
        agents_dir: 目标 ``.agents/`` 目录。
        world_toml_path: world.toml 文件路径。
        force: 是否强制覆盖已存在文件。
        no_hooks: 是否跳过生命周期钩子。

    Returns:
        进程退出码：``0`` 安装成功，``1`` 注册或其他异常，
        ``2`` 文件放置阶段错误。
    """
    print(
        f"Installing {manifest.name}@{manifest.version} from {source_path}...",
    )
    print()
    print("Compatibility check: all passed (L1-L4)")
    print()

    context = PlaceContext()

    try:
        installed_files = place_fragment(
            manifest,
            source_path,
            agents_dir,
            force=force,
            context=context,
        )
    except PlaceError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Error during file placement: {exc}", file=sys.stderr)
        rollback(context)
        return 1

    try:
        register_fragment(manifest, world_toml_path)
    except Exception as exc:  # noqa: BLE001 - 注册失败统一回滚
        print(f"Error during world.toml registration: {exc}", file=sys.stderr)
        print("Rolling back...")
        rollback(context)
        # 确保 world.toml 中没有残留条目
        try:
            unregister_fragment(manifest.name, world_toml_path)
        except OSError:
            pass
        return 1

    if not no_hooks:
        execute_lifecycle_hooks(manifest, agents_dir, "post-install")

    print(f"Installed {len(installed_files)} files:")
    for f in installed_files:
        try:
            rel = f.relative_to(agents_dir)
        except ValueError:
            rel = f
        print(f"  {rel}")
    print()
    print(
        f"Registered in world.toml: [fragments.{manifest.name}]"
        f" v{manifest.version}",
    )
    print()
    print("Done.")
    return 0
