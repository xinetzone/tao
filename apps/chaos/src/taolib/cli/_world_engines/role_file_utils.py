"""Role file utilities: frontmatter extraction and role file lookup.

本模块提供角色文件处理的通用工具函数，供 ``routing_engine``、
``role_resolver`` 等模块共同使用。

仅依赖标准库（``pathlib``）。
"""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "extract_frontmatter",
    "find_role_file",
]


def extract_frontmatter(text: str) -> str | None:
    """提取 ``+++`` 包围的 TOML frontmatter 文本。

    Args:
        text: 完整 Markdown 文件内容。

    Returns:
        frontmatter 主体（不含分隔符）；缺失时返回 ``None``。
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "+++":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "+++":
            return "\n".join(lines[1:idx])
    return None


def find_role_file(roles_dir: Path, role_id: str) -> Path | None:
    """在 governance/ 和 engineering/ 子目录中查找角色文件。

    搜索顺序：
    1. ``roles_dir/governance/{role_id}.md``
    2. ``roles_dir/engineering/{role_id}.md``
    3. ``roles_dir/{role_id}.md`` （兼容扁平结构过渡期）

    Args:
        roles_dir: ``roles/`` 目录路径。
        role_id: 角色 id（kebab-case）。

    Returns:
        找到的角色文件路径；不存在时返回 ``None``。
    """
    for subdir in ("governance", "engineering"):
        candidate = roles_dir / subdir / f"{role_id}.md"
        if candidate.exists():
            return candidate
    flat = roles_dir / f"{role_id}.md"
    return flat if flat.exists() else None
