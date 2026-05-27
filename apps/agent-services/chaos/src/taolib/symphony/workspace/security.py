"""工作区路径安全工具。

提供标识符净化、路径包含检查和符号链接解析，
确保编码智能体仅在授权的工作区根目录内操作，防止路径遍历攻击。

包含对 `tests/chaos` 目录的访问控制机制，
要求用户明确授权后才能访问该目录。
"""

import os
from pathlib import Path

__all__ = [
    "canonicalize",
    "sanitize_identifier",
    "assert_within_root",
    "assert_chaos_access",
    "set_chaos_access_allowed",
    "is_chaos_access_allowed",
]

# 仅允许 [A-Za-z0-9._-]，其余替换为 _
_SAFE_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
)

# 受保护目录 - tests/chaos 及其子目录
# 这些目录需要用户明确授权才能访问
_PROTECTED_DIRS: tuple[str, ...] = (
    "tests/chaos",
    "tests/chaos/",
)

# 全局状态：是否允许访问 chaos 目录
_chaos_access_allowed: bool = False


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
        msg = f"路径脱离工作区根目录: {canonical_path} 不在 {canonical_root} 内"
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


def is_chaos_access_allowed() -> bool:
    """检查是否已获得访问 chaos 目录的授权。

    Returns:
        如果允许访问返回 True，否则返回 False。
    """
    return _chaos_access_allowed


def set_chaos_access_allowed(allowed: bool) -> None:
    """设置是否允许访问 chaos 目录。

    Args:
        allowed: True 表示允许访问，False 表示禁止访问。
    """
    global _chaos_access_allowed
    _chaos_access_allowed = allowed


def _is_protected_path(path: Path) -> bool:
    """判断路径是否属于受保护的 chaos 目录。

    Args:
        path: 待检查的路径。

    Returns:
        如果路径属于受保护目录返回 True，否则返回 False。
    """
    path_str = str(path.resolve()).replace("\\", "/")
    for protected in _PROTECTED_DIRS:
        protected_clean = protected.rstrip("/")
        if f"/{protected_clean}" in path_str or path_str.endswith(
            f"/{protected_clean}"
        ):
            return True
    return False


def assert_chaos_access(path: Path) -> None:
    """验证对 chaos 目录的访问权限。

    如果路径涉及受保护的 `tests/chaos` 目录，
    且未获得用户明确授权，则抛出 ValueError。

    Args:
        path: 待检查的路径。

    Raises:
        ValueError: 路径涉及受保护目录且未获得授权。
    """
    if _is_protected_path(path):
        if not _chaos_access_allowed:
            msg = (
                f"禁止访问受保护目录: {path}\n"
                "该目录 (`tests/chaos`) 需要用户明确授权才能访问。\n"
                "请先通过 `set_chaos_access_allowed(True)` 授权，"
                "或使用相关命令导航进入该目录后再进行操作。"
            )
            raise ValueError(msg)
