"""工作区路径安全工具。

提供标识符净化、路径包含检查和符号链接解析，
确保编码智能体仅在授权的工作区根目录内操作，防止路径遍历攻击。
"""

import os
from pathlib import Path

__all__ = ["canonicalize", "sanitize_identifier", "assert_within_root"]

# 仅允许 [A-Za-z0-9._-]，其余替换为 _
_SAFE_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
)


def sanitize_identifier(identifier: str) -> str:
    """净化标识符，仅保留安全字符。

    将不在 [A-Za-z0-9._-] 范围内的字符替换为 ``_``，
    并去除首尾的 ``.`` 和 ``-`` 以避免隐藏文件或选项参数。

    Args:
        identifier: 原始标识符（如 Linear issue 标识）。

    Returns:
        净化后的安全字符串。
    """
    sanitized = "".join(ch if ch in _SAFE_CHARS else "_" for ch in identifier)
    # 去除首尾的 . 和 -，避免隐藏文件或选项参数
    sanitized = sanitized.strip(".-")
    if not sanitized:
        sanitized = "_empty_"
    return sanitized


def assert_within_root(path: Path, root: Path) -> None:
    """验证路径在根目录内，防止路径遍历。

    使用 canonicalize 逐段解析符号链接后进行比较，
    同时检查路径是否等于根目录（workspace_equals_root）。

    Args:
        path: 待检查的路径。
        root: 根目录路径。

    Raises:
        ValueError: 路径脱离根目录或路径等于根目录。
    """
    canonical_path = canonicalize(path)
    canonical_root = canonicalize(root)

    # 检查路径是否等于根目录
    if canonical_path == canonical_root:
        msg = f"工作区路径等于根目录: {path}"
        raise ValueError(msg)

    # 检查路径是否在根目录内
    try:
        canonical_path.relative_to(canonical_root)
    except ValueError:
        # 额外检查是否通过符号链接逃逸
        resolved_path = path.resolve()
        resolved_root = root.resolve()
        if resolved_path != resolved_root:
            try:
                resolved_path.relative_to(resolved_root)
            except ValueError:
                msg = (
                    f"路径脱离工作区根目录（符号链接逃逸）: {resolved_path} "
                    f"不在 {resolved_root} 内"
                )
                raise ValueError(msg) from None
        msg = (
            f"路径脱离工作区根目录: {canonical_path} "
            f"不在 {canonical_root} 内"
        )
        raise ValueError(msg)


def canonicalize(path: Path) -> Path:
    """逐段解析符号链接，返回规范化绝对路径。

    参考 Elixir PathSafety.canonicalize 实现。
    与 Path.resolve() 的区别：resolve() 仅解析最终目标，
    本函数逐段解析，确保中间符号链接不逃逸根目录。

    Args:
        path: 待规范化的路径。

    Returns:
        逐段解析后的绝对路径。
    """
    resolved = path.resolve()
    parts = resolved.parts
    result = Path(parts[0])  # 根路径（/ 或 C:\）

    for segment in parts[1:]:
        candidate = result / segment
        if candidate.is_symlink():
            target = Path(os.readlink(candidate))
            if not target.is_absolute():
                target = result / target
            # 递归解析符号链接链
            result = canonicalize(target)
        elif candidate.exists():
            result = candidate
        else:
            # 不存在的路径段保持原样
            result = candidate

    return result
