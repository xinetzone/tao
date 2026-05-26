"""Fragment 文件安装管理器。

负责将 Fragment 源文件复制到 ``.agents/`` 目录，并提供原子回滚能力。
"""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from taolib.cli._world_engines.manifest_parser import FragmentManifest


class PlaceError(Exception):
    """文件放置错误（如冲突、源文件缺失、权限不足等）。"""


@dataclass
class PlaceContext:
    """安装上下文，用于回滚追踪。

    Attributes:
        installed_files: 已成功复制到目标位置的文件 / 目录列表。
        backup_mapping: ``目标路径 -> 备份路径`` 的映射，用于在 ``force`` 模式
            下覆盖前保留旧文件。
        backup_dir: 临时备份目录，回滚结束后会被清理。
    """

    installed_files: list[Path] = field(default_factory=list)
    backup_mapping: dict[Path, Path] = field(default_factory=dict)
    backup_dir: Path | None = None


def _iter_manifest_entries(manifest: FragmentManifest) -> list[str]:
    """收集 manifest.contents 中所有待安装条目的相对路径。

    Args:
        manifest: 解析后的 Fragment manifest。

    Returns:
        合并后的相对路径列表，顺序为 ``rules``、``skills``、``scripts``、
        ``docs``、``templates``。
    """
    contents = manifest.contents
    entries: list[str] = []
    entries.extend(contents.rules)
    entries.extend(contents.skills)
    entries.extend(contents.scripts)
    entries.extend(contents.docs)
    entries.extend(contents.templates)
    return entries


def _is_dir_entry(rel_path: str) -> bool:
    """判断 manifest 中的相对路径是否表示一个目录。

    约定以 ``/`` 或 ``\\`` 结尾的条目为目录条目。
    """
    return rel_path.endswith(("/", "\\"))


def place_fragment(
    manifest: FragmentManifest,
    source_path: Path,
    agents_dir: Path,
    force: bool = False,
    context: PlaceContext | None = None,
) -> list[Path]:
    """将 Fragment 文件复制到 ``.agents/`` 目录。

    流程：

    1. 收集 ``manifest.contents`` 中所有相对路径条目；
    2. 预检阶段：校验每个源文件存在，若目标已存在且未启用 ``force``，
       则抛出 :class:`PlaceError`；
    3. 若启用 ``force`` 且存在冲突文件，则将其备份到临时目录；
    4. 创建必要的父目录后，按目录 / 文件类型分别使用
       :func:`shutil.copytree` 或 :func:`shutil.copy2` 复制；
    5. 将每次成功复制的目标路径追加至 ``context.installed_files``。

    Args:
        manifest: 解析后的 Fragment manifest。
        source_path: Fragment 源根目录（包含 manifest 描述的相对路径）。
        agents_dir: 目标 ``.agents/`` 目录。
        force: 是否强制覆盖已存在的目标文件。
        context: 可选的 :class:`PlaceContext`，用于在外部进行回滚追踪。
            未传入时函数会创建新的上下文，但仅返回安装文件列表。

    Returns:
        所有成功复制到目标位置的路径列表（与 ``context.installed_files``
        保持一致）。

    Raises:
        PlaceError: 源文件缺失，或目标存在冲突且未启用 ``force`` 时抛出。
    """
    if context is None:
        context = PlaceContext()

    entries = _iter_manifest_entries(manifest)

    # 预检阶段：分别收集缺失源、冲突目标
    missing_sources: list[Path] = []
    conflicts: list[Path] = []
    plan: list[tuple[str, Path, Path]] = []

    for rel_path in entries:
        normalized = rel_path.rstrip("/\\")
        src = source_path / normalized
        dst = agents_dir / normalized

        if not src.exists():
            missing_sources.append(src)
            continue

        if dst.exists() and not force:
            conflicts.append(dst)

        plan.append((rel_path, src, dst))

    if missing_sources:
        listing = "\n  - ".join(str(p) for p in missing_sources)
        raise PlaceError(
            f"Fragment '{manifest.name}' 缺失源文件：\n  - {listing}",
        )

    if conflicts:
        listing = "\n  - ".join(str(p) for p in conflicts)
        raise PlaceError(
            f"Fragment '{manifest.name}' 目标已存在 {len(conflicts)} 个冲突"
            f"文件，使用 --force 覆盖：\n  - {listing}",
        )

    # force 模式下备份已存在文件
    if force and any(dst.exists() for _, _, dst in plan):
        context.backup_dir = Path(
            tempfile.mkdtemp(prefix=f"agentforge-backup-{manifest.name}-"),
        )
        for _, _, dst in plan:
            if not dst.exists():
                continue
            backup_target = context.backup_dir / dst.name
            counter = 0
            while backup_target.exists():
                counter += 1
                backup_target = (
                    context.backup_dir / f"{dst.name}.{counter}"
                )
            if dst.is_dir():
                shutil.copytree(dst, backup_target)
            else:
                shutil.copy2(dst, backup_target)
            context.backup_mapping[dst] = backup_target

    # 实际复制阶段
    for rel_path, src, dst in plan:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if _is_dir_entry(rel_path) or src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        context.installed_files.append(dst)

    return context.installed_files


def rollback(context: PlaceContext) -> None:
    """回滚一次失败 / 中止的 :func:`place_fragment` 调用。

    流程：

    1. 逆序删除 ``context.installed_files`` 中的目标文件 / 目录；
    2. 删除已变空的父目录（直至遇到非空目录或越过备份/源目录范围）；
    3. 若存在备份映射，将备份恢复至原位置；
    4. 清理临时备份目录。

    Args:
        context: 由 :func:`place_fragment` 填充的安装上下文。
    """
    for path in reversed(context.installed_files):
        try:
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists() or path.is_symlink():
                path.unlink(missing_ok=True)
        except OSError:
            continue

        # 清理空父目录
        parent = path.parent
        while parent.exists() and parent.is_dir():
            try:
                next(parent.iterdir())
            except StopIteration:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
            else:
                break

    context.installed_files.clear()

    # 恢复备份
    for target, backup in context.backup_mapping.items():
        if not backup.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink(missing_ok=True)
        if backup.is_dir():
            shutil.copytree(backup, target)
        else:
            shutil.copy2(backup, target)

    context.backup_mapping.clear()

    # 清理备份目录
    if context.backup_dir is not None and context.backup_dir.exists():
        shutil.rmtree(context.backup_dir, ignore_errors=True)
    context.backup_dir = None
