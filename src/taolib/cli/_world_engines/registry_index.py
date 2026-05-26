"""Registry Index 查询 — 加载和查询 Registry Index 中的组件条目。"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from taolib.cli._world_engines.compat_engine import matches_constraint
from taolib.cli._world_engines.registry_config import RegistrySource


@dataclass(frozen=True)
class IndexVersion:
    """Index 条目中的版本记录。"""

    version: str
    git_url: str
    git_ref: str
    manifest_path: str = "manifest.toml"
    checksum: str | None = None
    yanked: bool = False


@dataclass(frozen=True)
class IndexEntry:
    """Index 中的完整条目。"""

    name: str
    description: str
    category: str
    entry_type: str  # "fragment" | "skill" | "script" | "template"
    source_repository: str
    versions: list[IndexVersion] = field(default_factory=list)
    latest_stable: str = ""


def _is_remote_url(url: str) -> bool:
    """判断 URL 是否为远程地址。"""
    return url.startswith(("http://", "https://", "git://", "ssh://", "git@"))


def _version_tuple(version: str) -> tuple[int, ...]:
    """将版本号解析为整数元组以便比较。

    若解析失败（如包含非数字段），回退到 ``(0,)``。
    """
    try:
        return tuple(int(p) for p in version.split("."))
    except ValueError:
        return (0,)


def resolve_index_path(source: RegistrySource) -> Path | None:
    """解析 Registry 源到本地 Index 目录路径。

    Args:
        source: Registry 源配置。

    Returns:
        - 若 ``source.url`` 为本地相对/绝对路径且存在：返回绝对路径。
        - 若 ``source.url`` 为远程 URL：本次实现暂不处理，返回 ``None``。
        - 路径不存在时返回 ``None``。
    """
    url = source.url
    if not url:
        return None

    if _is_remote_url(url):
        # 远程 URL 的本地缓存暂未实现
        return None

    candidate = Path(url)
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.exists() or not candidate.is_dir():
        return None

    return candidate


def _parse_index_toml(path: Path) -> IndexEntry | None:
    """解析单个 Index 条目 TOML 文件。"""
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None

    metadata = data.get("metadata", {})
    name = metadata.get("name", "")
    if not name:
        return None

    source = data.get("source", {})
    versions_data = data.get("versions", [])
    versions: list[IndexVersion] = []
    for v in versions_data:
        if not isinstance(v, dict):
            continue
        version_str = v.get("version", "")
        if not version_str:
            continue
        versions.append(
            IndexVersion(
                version=version_str,
                git_url=v.get("git_url", ""),
                git_ref=v.get("git_ref", ""),
                manifest_path=v.get("manifest_path", "manifest.toml"),
                checksum=v.get("checksum"),
                yanked=bool(v.get("yanked", False)),
            ),
        )

    latest = data.get("latest", {})
    latest_stable = latest.get("stable", "")

    return IndexEntry(
        name=name,
        description=metadata.get("description", ""),
        category=metadata.get("category", ""),
        entry_type=metadata.get("type", "fragment"),
        source_repository=source.get("repository", ""),
        versions=versions,
        latest_stable=latest_stable,
    )


def query_entry(
    index_path: Path,
    name: str,
    entry_type: str = "fragment",
) -> IndexEntry | None:
    """在 Registry Index 中查询指定名称的条目。

    Args:
        index_path: Registry Index 根目录。
        name: 条目名称。
        entry_type: 条目类型，决定搜索的子目录（``fragment`` → ``fragments/``）。

    Returns:
        匹配的 :class:`IndexEntry`，未找到时返回 ``None``。
    """
    if not index_path.exists() or not index_path.is_dir():
        return None

    type_dir = index_path / f"{entry_type}s"
    if not type_dir.exists() or not type_dir.is_dir():
        return None

    # 遍历所有分类子目录查找 {name}.toml
    for toml_file in type_dir.glob(f"*/{name}.toml"):
        if toml_file.is_file():
            entry = _parse_index_toml(toml_file)
            if entry is not None and entry.name == name:
                return entry

    # 兼容直接放在 type_dir 下的情况
    direct = type_dir / f"{name}.toml"
    if direct.is_file():
        entry = _parse_index_toml(direct)
        if entry is not None and entry.name == name:
            return entry

    return None


def select_version(
    entry: IndexEntry,
    constraint: str | None,
) -> IndexVersion | None:
    """根据版本约束从 IndexEntry 中选择最佳版本。

    选择策略：

    1. ``constraint`` 为 ``None``：返回 ``latest_stable`` 对应版本。
    2. ``constraint`` 为约束表达式：使用
       :func:`compat_engine.matches_constraint` 过滤，取最大兼容版本。
    3. 所有情况下跳过 ``yanked=True`` 的版本。
    4. 未找到匹配版本返回 ``None``。

    Args:
        entry: Index 条目。
        constraint: 版本约束字符串，``None`` 表示选择 latest_stable。

    Returns:
        匹配的 :class:`IndexVersion`，未找到时返回 ``None``。
    """
    available = [v for v in entry.versions if not v.yanked]
    if not available:
        return None

    if constraint is None:
        if not entry.latest_stable:
            return None
        for v in available:
            if v.version == entry.latest_stable:
                return v
        return None

    matched: list[IndexVersion] = []
    for v in available:
        try:
            if matches_constraint(v.version, constraint):
                matched.append(v)
        except Exception:
            # 版本字符串不规范时跳过
            continue

    if not matched:
        return None

    matched.sort(key=lambda v: _version_tuple(v.version), reverse=True)
    return matched[0]
