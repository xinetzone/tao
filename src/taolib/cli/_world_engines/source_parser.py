"""Source 参数解析器 — 识别 install 命令的 source 类型。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SourceType(Enum):
    """install 命令 source 参数的类型。"""

    LOCAL = "local"
    REGISTRY = "registry"
    GIT_URL = "git_url"


@dataclass(frozen=True)
class ParsedSource:
    """解析后的 source 参数。"""

    source_type: SourceType
    raw: str
    name: str | None = None  # registry 类型时的组件名
    constraint: str | None = None  # registry 类型时的版本约束（None 表示取 latest.stable）
    url: str | None = None  # git_url 类型时的 URL
    ref: str | None = None  # git_url 类型时的 ref


def _is_git_url(source: str) -> bool:
    """判断 source 是否为 Git URL 形式。"""
    return (
        source.startswith("https://")
        or source.startswith("http://")
        or source.startswith("git@")
    )


def _is_local_path_prefix(source: str) -> bool:
    """判断 source 是否以本地路径前缀开头。"""
    return (
        source.startswith("./")
        or source.startswith("../")
        or source.startswith("/")
        or source.startswith("\\")
    )


def parse_source(source: str) -> ParsedSource:
    """解析 source 参数，区分本地 / registry / git URL。

    解析优先级规则（对齐 CLI 规格）：

    1. ``https://`` / ``http://`` / ``git@`` 开头 → :attr:`SourceType.GIT_URL`
    2. ``./`` / ``../`` / ``/`` / ``\\`` 开头 → :attr:`SourceType.LOCAL`
    3. 含 ``@`` 且无 ``//`` → :attr:`SourceType.REGISTRY` （``name@constraint``）
    4. 路径存在于文件系统 → :attr:`SourceType.LOCAL`
    5. 其余 → :attr:`SourceType.REGISTRY` （仅 ``name``，``constraint=None`` 表示 ``latest.stable``）

    Args:
        source: 待解析的原始字符串。

    Returns:
        解析后的 :class:`ParsedSource` 实例。
    """
    # 1. Git URL（必须先于 @ 判断，避免 git@... 被误识别为 registry）
    if _is_git_url(source):
        return ParsedSource(
            source_type=SourceType.GIT_URL,
            raw=source,
            url=source,
            ref=None,
        )

    # 2. 显式本地路径前缀
    if _is_local_path_prefix(source):
        return ParsedSource(source_type=SourceType.LOCAL, raw=source)

    # 3. registry 形式：name@constraint（排除含 // 的 URL 形式）
    if "@" in source and "//" not in source:
        name, _, constraint = source.partition("@")
        return ParsedSource(
            source_type=SourceType.REGISTRY,
            raw=source,
            name=name,
            constraint=constraint or None,
        )

    # 4. 路径已存在于文件系统
    try:
        if Path(source).exists():
            return ParsedSource(source_type=SourceType.LOCAL, raw=source)
    except OSError:
        # 非法路径字符等情况，回退到 registry 解析
        pass

    # 5. 默认视为仅 name 的 registry 引用
    return ParsedSource(
        source_type=SourceType.REGISTRY,
        raw=source,
        name=source,
        constraint=None,
    )
