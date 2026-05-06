"""工作区路径安全工具。

提供标识符净化和路径包含检查，确保编码智能体
仅在授权的工作区根目录内操作，防止路径遍历攻击。
"""

from pathlib import Path

__all__ = ["sanitize_identifier", "assert_within_root"]

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

    递归解析符号链接后进行比较，确保规范化路径
    是根目录的子路径。

    Args:
        path: 待检查的路径。
        root: 根目录路径。

    Raises:
        ValueError: 路径脱离根目录。
    """
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError:
        msg = (
            f"路径脱离工作区根目录: {resolved_path} "
            f"不在 {resolved_root} 内"
        )
        raise ValueError(msg)
