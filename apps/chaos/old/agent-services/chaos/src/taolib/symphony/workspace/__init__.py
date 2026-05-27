"""工作区管理子包。

提供工作区创建、复用、清理及路径安全保障。

包含对 `tests/chaos` 目录的访问控制机制，
要求用户明确授权后才能访问该目录。
"""

from .manager import HooksConfig, Workspace, WorkspaceManager
from .security import (
    assert_chaos_access,
    is_chaos_access_allowed,
    set_chaos_access_allowed,
)

__all__ = [
    "WorkspaceManager",
    "Workspace",
    "HooksConfig",
    "assert_chaos_access",
    "is_chaos_access_allowed",
    "set_chaos_access_allowed",
]
