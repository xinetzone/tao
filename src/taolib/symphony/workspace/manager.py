"""工作区管理器。

为每个 Issue 创建隔离的文件系统工作区，
支持生命周期钩子（after_create / before_remove），
并通过路径安全工具防止遍历攻击。
"""

from dataclasses import dataclass
from pathlib import Path

from ..errors import HookError
from .hooks import HookTimeoutError, run_hook
from .security import assert_within_root, sanitize_identifier

__all__ = ["Workspace", "WorkspaceManager"]


@dataclass(frozen=True)
class Workspace:
    """工作区描述。"""

    path: Path
    """工作区在文件系统上的绝对路径。"""

    workspace_key: str
    """净化后的标识符键名。"""

    created_now: bool
    """是否为本次调用新创建（False 表示复用已有目录）。"""


@dataclass
class HooksConfig:
    """工作区钩子配置。"""

    after_create: str | None = None
    """工作区创建后执行的脚本。"""

    before_remove: str | None = None
    """工作区删除前执行的脚本。"""

    timeout_ms: int = 30_000
    """钩子执行超时（毫秒）。"""


class WorkspaceManager:
    """工作区生命周期管理器。

    为每个 Issue 标识符创建或复用独立的文件系统目录，
    并在关键节点执行配置的钩子脚本。
    """

    def __init__(self, root: Path, hooks_config: HooksConfig | None = None) -> None:
        self._root = root.resolve()
        self._hooks = hooks_config or HooksConfig()

    @property
    def root(self) -> Path:
        """工作区根目录。"""
        return self._root

    async def create_for_issue(self, identifier: str) -> Workspace:
        """创建或重用工作区。

        如果工作区目录已存在则复用（``created_now=False``），
        否则创建新目录并执行 ``after_create`` 钩子。

        Args:
            identifier: Issue 标识符（如 Linear issue 标识）。

        Returns:
            工作区描述对象。

        Raises:
            ValueError: 净化后的路径脱离根目录。
            HookTimeoutError: 钩子执行超时。
            HookError: 钩子执行失败。
        """
        workspace_key = sanitize_identifier(identifier)
        workspace_path = self._root / workspace_key
        assert_within_root(workspace_path, self._root)

        created_now = not workspace_path.exists()
        workspace_path.mkdir(parents=True, exist_ok=True)

        if created_now and self._hooks.after_create:
            await run_hook(
                self._hooks.after_create,
                workspace_path,
                self._hooks.timeout_ms,
            )

        return Workspace(
            path=workspace_path,
            workspace_key=workspace_key,
            created_now=created_now,
        )

    async def cleanup_workspace(self, identifier: str) -> None:
        """清理工作区（执行 before_remove 钩子后删除）。

        Args:
            identifier: Issue 标识符。

        Raises:
            ValueError: 净化后的路径脱离根目录。
            HookTimeoutError: 钩子执行超时。
            HookError: 钩子执行失败。
        """
        import shutil

        workspace_key = sanitize_identifier(identifier)
        workspace_path = self._root / workspace_key
        assert_within_root(workspace_path, self._root)

        if not workspace_path.exists():
            return

        if self._hooks.before_remove:
            await run_hook(
                self._hooks.before_remove,
                workspace_path,
                self._hooks.timeout_ms,
            )

        shutil.rmtree(workspace_path)

    def list_workspaces(self) -> list[str]:
        """列出根目录下所有工作区键名。"""
        if not self._root.exists():
            return []
        return [
            p.name
            for p in self._root.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ]

    def workspace_exists(self, identifier: str) -> bool:
        """检查指定标识符的工作区是否已存在。"""
        workspace_key = sanitize_identifier(identifier)
        workspace_path = self._root / workspace_key
        return workspace_path.exists()
