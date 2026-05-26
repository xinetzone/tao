"""world.lock 生成与解析引擎。"""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class LockPackage:
    """锁定文件中的单个包记录。"""

    name: str
    version: str
    type: str  # "fragment" | "skill" | "script" | "template"
    source: str  # "registry+<name>" | "git+<url>" | "local+<path>"
    git_url: str
    git_ref: str
    checksum: str | None = None
    dependencies: list[str] = field(default_factory=list)  # ["citations@>=1.0.0"]


@dataclass(frozen=True)
class LockFile:
    """world.lock 的完整表示。"""

    generated: str  # ISO 8601 UTC
    resolver_version: str  # "1"
    world_toml_hash: str  # "sha256:..."
    packages: list[LockPackage] = field(default_factory=list)


def compute_world_toml_hash(world_toml_path: Path) -> str:
    """计算 world.toml 的 SHA256 哈希。

    Args:
        world_toml_path: world.toml 的文件路径。

    Returns:
        ``sha256:<hex>`` 格式的哈希字符串。
    """
    content = world_toml_path.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    return f"sha256:{digest}"


def _escape_toml_string(value: str) -> str:
    """转义 TOML 基础字符串中的特殊字符。"""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _format_toml_string_list(items: list[str]) -> str:
    """将字符串列表格式化为 TOML 内联数组字面量。"""
    if not items:
        return "[]"
    quoted = ", ".join(f'"{_escape_toml_string(item)}"' for item in items)
    return f"[{quoted}]"


def generate_lock(lock: LockFile, output_path: Path) -> None:
    """将 LockFile 序列化为 TOML 格式写入文件。

    输出格式遵循手动构建 TOML 字符串的风格（与项目中
    world_updater.py 一致），不使用 tomlkit。

    Args:
        lock: 待序列化的 :class:`LockFile` 实例。
        output_path: 输出文件路径（通常为 ``.agents/world.lock``）。
    """
    lines: list[str] = []

    # 固定注释头
    lines.append("# world.lock — 自动生成，请勿手动修改")
    lines.append("")

    # [lock] 段
    lines.append("[lock]")
    lines.append(f'generated = "{_escape_toml_string(lock.generated)}"')
    lines.append(f'resolver-version = "{_escape_toml_string(lock.resolver_version)}"')
    lines.append(f'world-toml-hash = "{_escape_toml_string(lock.world_toml_hash)}"')

    # [[packages]] 段
    for pkg in lock.packages:
        lines.append("")
        lines.append("[[packages]]")
        lines.append(f'name = "{_escape_toml_string(pkg.name)}"')
        lines.append(f'version = "{_escape_toml_string(pkg.version)}"')
        lines.append(f'type = "{_escape_toml_string(pkg.type)}"')
        lines.append(f'source = "{_escape_toml_string(pkg.source)}"')
        lines.append(f'git_url = "{_escape_toml_string(pkg.git_url)}"')
        lines.append(f'git_ref = "{_escape_toml_string(pkg.git_ref)}"')
        if pkg.checksum is not None:
            lines.append(f'checksum = "{_escape_toml_string(pkg.checksum)}"')
        lines.append(f"dependencies = {_format_toml_string_list(pkg.dependencies)}")

    # 写入文件（末尾换行）
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_lock(path: Path) -> LockFile | None:
    """读取并解析 world.lock 文件。

    Args:
        path: world.lock 的文件路径。

    Returns:
        解析后的 :class:`LockFile` 实例，文件不存在或格式错误返回 ``None``。
    """
    if not path.exists():
        return None

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None

    lock_data = data.get("lock")
    if not isinstance(lock_data, dict):
        return None

    generated = lock_data.get("generated", "")
    resolver_version = lock_data.get("resolver-version", "")
    world_toml_hash = lock_data.get("world-toml-hash", "")

    packages_data = data.get("packages", [])
    packages: list[LockPackage] = []
    for pkg_data in packages_data:
        if not isinstance(pkg_data, dict):
            continue
        name = pkg_data.get("name", "")
        if not name:
            continue
        packages.append(
            LockPackage(
                name=name,
                version=pkg_data.get("version", ""),
                type=pkg_data.get("type", "fragment"),
                source=pkg_data.get("source", ""),
                git_url=pkg_data.get("git_url", ""),
                git_ref=pkg_data.get("git_ref", ""),
                checksum=pkg_data.get("checksum"),
                dependencies=pkg_data.get("dependencies", []),
            ),
        )

    return LockFile(
        generated=generated,
        resolver_version=resolver_version,
        world_toml_hash=world_toml_hash,
        packages=packages,
    )
