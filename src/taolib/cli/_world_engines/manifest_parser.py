from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class KernelCompat:
    """Kernel 版本兼容性约束。"""

    min_version: str
    max_version: str  # 排他上界


@dataclass(frozen=True)
class FragmentContents:
    """Fragment 包含的文件清单。"""

    rules: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    docs: list[str] = field(default_factory=list)
    templates: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class FragmentManifest:
    """解析后的 Fragment manifest。"""

    name: str
    version: str
    description: str
    kernel_compat: KernelCompat | None = None
    dependencies: dict[str, str] = field(default_factory=dict)
    conflicts: dict[str, str] = field(default_factory=dict)
    contents: FragmentContents = field(default_factory=FragmentContents)
    hooks: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InstalledFragment:
    """world.toml 中已安装的 Fragment 信息。"""

    name: str
    version: str
    optional: bool = True


@dataclass(frozen=True)
class WorldInfo:
    """world.toml 中的世界基本信息。"""

    name: str
    version: str
    fragments: list[InstalledFragment] = field(default_factory=list)


def parse_manifest(path: Path) -> FragmentManifest:
    """解析 Fragment 的 manifest.toml 文件。

    Args:
        path: manifest.toml 的文件路径。

    Returns:
        解析后的 :class:`FragmentManifest` 实例。
    """
    with path.open("rb") as f:
        data = tomllib.load(f)

    fragment = data.get("fragment", {})
    name = fragment.get("name", "")
    version = fragment.get("version", "")
    description = fragment.get("description", "")

    kernel_compat = None
    compat_data = fragment.get("kernel-compat", {})
    if compat_data:
        min_v = compat_data.get("min-version")
        max_v = compat_data.get("max-version")
        if min_v and max_v:
            kernel_compat = KernelCompat(min_version=min_v, max_version=max_v)

    dependencies = dict(fragment.get("dependencies", {}))
    conflicts = dict(fragment.get("conflicts", {}))

    contents_data = fragment.get("contents", {})
    contents = FragmentContents(
        rules=contents_data.get("rules", []),
        skills=contents_data.get("skills", []),
        scripts=contents_data.get("scripts", []),
        docs=contents_data.get("docs", []),
        templates=contents_data.get("templates", []),
    )

    hooks = dict(fragment.get("hooks", {}))

    return FragmentManifest(
        name=name,
        version=version,
        description=description,
        kernel_compat=kernel_compat,
        dependencies=dependencies,
        conflicts=conflicts,
        contents=contents,
        hooks=hooks,
    )


def parse_world_toml(path: Path) -> WorldInfo:
    """解析 world.toml 文件，提取世界基本信息与已安装 Fragment 列表。

    Args:
        path: world.toml 的文件路径。

    Returns:
        解析后的 :class:`WorldInfo` 实例。
    """
    with path.open("rb") as f:
        data = tomllib.load(f)

    world_data = data.get("world", {})
    name = world_data.get("name", "")
    version = world_data.get("version", "")

    fragments: list[InstalledFragment] = []
    fragments_data = data.get("fragments", {})
    for frag_name, frag_info in fragments_data.items():
        if isinstance(frag_info, dict):
            frag_version = frag_info.get("version", "")
            optional = frag_info.get("optional", True)
            fragments.append(
                InstalledFragment(
                    name=frag_name,
                    version=frag_version,
                    optional=optional,
                ),
            )

    return WorldInfo(name=name, version=version, fragments=fragments)


def find_world_toml(start: Path | None = None) -> Path | None:
    """从起始目录向上递归查找 ``.agents/world.toml``。

    Args:
        start: 起始目录，默认为当前工作目录。

    Returns:
        找到的 world.toml 路径，若未找到则返回 ``None``。
    """
    if start is None:
        start = Path.cwd()
    current = start.resolve()

    for parent in [current, *current.parents]:
        candidate = parent / ".agents" / "world.toml"
        if candidate.exists():
            return candidate

    return None
