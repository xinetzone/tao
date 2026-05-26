from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .._world_engines.compat_engine import ValidationLevel, validate
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
from .._world_engines.world_updater import register_fragment, unregister_fragment

_LEVEL_LABELS = {
    ValidationLevel.L1_KERNEL_COMPAT: "L1 Kernel compat",
    ValidationLevel.L2_CONFLICTS: "L2 Conflicts",
    ValidationLevel.L3_DEPENDENCIES: "L3 Dependencies",
    ValidationLevel.L4_FILE_CONFLICTS: "L4 File conflicts",
}


def _is_local_source(source: str) -> bool:
    """判断 source 是否为本地路径。

    原型阶段仅支持本地路径：以 ``./``、``/``、``\\`` 开头，
    或指向一个已存在的目录/文件。

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
    install_parser.add_argument("source", help="Fragment 源路径（本地目录）")
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


def handle_install(args: argparse.Namespace) -> int:
    """执行 ``world install`` 命令逻辑。

    完整流程：

    1. 验证 source 为本地路径并解析 ``manifest.toml``；
    2. 查找并解析 ``world.toml``；
    3. 确定 ``.agents/`` 目录；
    4. 调用四层兼容性校验；
    5. 若 ``--dry-run`` 则仅输出报告；否则在校验通过时执行
       文件放置 → world.toml 注册 → 生命周期钩子。

    Args:
        args: 已解析的命令行参数。

    Returns:
        进程退出码：``0`` 表示成功，``1`` 表示一般错误，
        ``2`` 表示校验失败或文件放置错误。
    """
    source = args.source

    if not _is_local_source(source):
        print(
            f"Error: source '{source}' is not a valid local path. "
            "Prototype only supports local directories.",
            file=sys.stderr,
        )
        return 1

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
