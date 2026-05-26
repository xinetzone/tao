"""world.toml Fragment 注册/注销管理器。

使用字符串追加方式更新 world.toml，避免引入额外 TOML 写入库。
"""

from __future__ import annotations

import re
from pathlib import Path

from taolib.cli._world_engines.manifest_parser import FragmentManifest

_FRAGMENT_SECTION_RE = re.compile(r"^\s*\[fragments\.([^\]]+)\]\s*$")
_ANY_SECTION_RE = re.compile(r"^\s*\[[^\]]+\]\s*$")


def register_fragment(manifest: FragmentManifest, world_toml_path: Path) -> None:
    """将 Fragment 注册到 world.toml。

    在 world.toml 中追加新的 ``[fragments.<name>]`` 段落，插入位置为
    最后一个 ``[fragments.*]`` 段之后。若 world.toml 中尚无任何 fragment
    段，则在 ``[capabilities]`` 段之前插入；若也不存在 ``[capabilities]``
    段，则追加到文件末尾。

    Args:
        manifest: 待注册 Fragment 的解析后 manifest。
        world_toml_path: 目标 world.toml 文件路径。

    Raises:
        ValueError: 当同名 Fragment 已存在时抛出，避免重复注册。
    """
    text = world_toml_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    if _find_fragment_section_start(lines, manifest.name) is not None:
        msg = f"Fragment '{manifest.name}' 已在 world.toml 中注册"
        raise ValueError(msg)

    new_section = _build_fragment_section(manifest)

    insert_index = _find_last_fragment_section_end(lines)
    if insert_index is None:
        insert_index = _find_capabilities_section_start(lines)
    if insert_index is None:
        insert_index = len(lines)

    block = _ensure_surrounding_blank_lines(lines, insert_index, new_section)
    new_lines = lines[:insert_index] + block + lines[insert_index:]
    world_toml_path.write_text("".join(new_lines), encoding="utf-8")


def unregister_fragment(name: str, world_toml_path: Path) -> None:
    """从 world.toml 中注销同名 Fragment。

    若指定 Fragment 不存在，则保持文件内容不变（静默返回）。删除时
    一并去除该段落紧随其后的空行，保持 TOML 结构整洁。

    Args:
        name: 待注销的 Fragment 名称。
        world_toml_path: 目标 world.toml 文件路径。
    """
    text = world_toml_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    start = _find_fragment_section_start(lines, name)
    if start is None:
        return

    end = _find_section_end(lines, start)
    while end < len(lines) and lines[end].strip() == "":
        end += 1

    new_lines = lines[:start] + lines[end:]
    world_toml_path.write_text("".join(new_lines), encoding="utf-8")


def _flatten_contents(manifest: FragmentManifest) -> list[str]:
    """将 :class:`FragmentContents` 的所有字段合并为扁平列表。

    Args:
        manifest: Fragment manifest。

    Returns:
        合并后的内容路径列表，顺序为 rules、skills、scripts、docs、
        templates。
    """
    contents = manifest.contents
    return [
        *contents.rules,
        *contents.skills,
        *contents.scripts,
        *contents.docs,
        *contents.templates,
    ]


def _find_last_fragment_section_end(lines: list[str]) -> int | None:
    """定位最后一个 ``[fragments.*]`` 段的结尾行号。

    Args:
        lines: world.toml 按行切分的内容。

    Returns:
        最后一个 fragment 段落结束后的行号（即新内容应插入的位置）。
        若没有任何 fragment 段，返回 ``None``。
    """
    last_start: int | None = None
    for idx, line in enumerate(lines):
        if _FRAGMENT_SECTION_RE.match(line):
            last_start = idx

    if last_start is None:
        return None

    return _find_section_end(lines, last_start)


def _find_fragment_section_start(lines: list[str], name: str) -> int | None:
    """查找指定 Fragment 段的起始行号。

    Args:
        lines: world.toml 按行切分的内容。
        name: Fragment 名称。

    Returns:
        ``[fragments.<name>]`` 行的索引，未找到则返回 ``None``。
    """
    for idx, line in enumerate(lines):
        match = _FRAGMENT_SECTION_RE.match(line)
        if match and match.group(1).strip() == name:
            return idx
    return None


def _find_section_end(lines: list[str], start: int) -> int:
    """查找 TOML 段落的结束行号（不含）。

    Args:
        lines: world.toml 按行切分的内容。
        start: 段落起始行（``[xxx]`` 所在行）。

    Returns:
        下一个段落起始行号，若无则返回 ``len(lines)``。
    """
    for idx in range(start + 1, len(lines)):
        if _ANY_SECTION_RE.match(lines[idx]):
            return idx
    return len(lines)


def _find_capabilities_section_start(lines: list[str]) -> int | None:
    """查找 ``[capabilities]`` 段的起始行号。

    Args:
        lines: world.toml 按行切分的内容。

    Returns:
        ``[capabilities]`` 行的索引，未找到则返回 ``None``。
    """
    for idx, line in enumerate(lines):
        if line.strip() == "[capabilities]":
            return idx
    return None


def _build_fragment_section(manifest: FragmentManifest) -> str:
    """构建 Fragment 的 TOML 段落字符串。

    Args:
        manifest: Fragment manifest。

    Returns:
        以换行结尾的多行 TOML 段落字符串。
    """
    contents = _flatten_contents(manifest)
    contents_literal = _format_toml_string_list(contents)

    lines = [
        f"[fragments.{manifest.name}]\n",
        f'version = "{_escape_toml_string(manifest.version)}"\n',
        f'description = "{_escape_toml_string(manifest.description)}"\n',
        "optional = true\n",
        f"contents = {contents_literal}\n",
    ]
    return "".join(lines)


def _format_toml_string_list(items: list[str]) -> str:
    """将字符串列表格式化为 TOML 内联数组字面量。

    Args:
        items: 字符串列表。

    Returns:
        TOML 数组字面量，例如 ``[]`` 或 ``["a", "b"]``。
    """
    if not items:
        return "[]"
    quoted = ", ".join(f'"{_escape_toml_string(item)}"' for item in items)
    return f"[{quoted}]"


def _escape_toml_string(value: str) -> str:
    """转义 TOML 基础字符串中的特殊字符。

    Args:
        value: 原始字符串。

    Returns:
        转义后的字符串，可安全嵌入双引号字符串字面量。
    """
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _ensure_surrounding_blank_lines(
    lines: list[str],
    insert_index: int,
    section: str,
) -> list[str]:
    """构建插入块，保证新段落与上下文之间至少有一个空行。

    Args:
        lines: 原文件按行切分的内容。
        insert_index: 计划插入位置。
        section: 待插入的段落字符串（已含末尾换行）。

    Returns:
        包含可选前导/尾随空行的行列表，可直接拼接进原内容。
    """
    block: list[str] = []

    prev_line = lines[insert_index - 1] if insert_index > 0 else ""
    if prev_line and prev_line.strip() != "":
        block.append("\n")

    block.append(section)

    next_line = lines[insert_index] if insert_index < len(lines) else ""
    if next_line and next_line.strip() != "":
        block.append("\n")

    return block
