"""Symphony 文件监视器。

基于 watchdog 监视 WORKFLOW.md 文件变更，
防抖后触发重新加载，验证失败时保持最后有效配置。
"""

import logging
import time
from pathlib import Path
from collections.abc import Callable

from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from taolib.symphony.config.loader import load_workflow
from taolib.symphony.config.schema import SymphonyConfig
from taolib.symphony.errors import WorkflowLoadError

logger = logging.getLogger(__name__)

# 防抖间隔（毫秒）
_DEBOUNCE_MS = 500

# 回调类型别名
OnReloadSuccess = Callable[[SymphonyConfig], None]
OnReloadError = Callable[[Exception], None]


class _WorkflowEventHandler(FileSystemEventHandler):
    """WORKFLOW.md 文件变更事件处理器。

    实现防抖逻辑：收到变更事件后等待 _DEBOUNCE_MS，
    如果期间没有新的变更事件则触发重新加载。
    """

    def __init__(
        self,
        workflow_path: Path,
        on_reload_success: OnReloadSuccess | None,
        on_reload_error: OnReloadError | None,
    ) -> None:
        super().__init__()
        self._workflow_path = workflow_path
        self._on_reload_success = on_reload_success
        self._on_reload_error = on_reload_error
        self._last_event_time: float = 0.0
        self._last_valid_config: SymphonyConfig | None = None
        self._debounce_seconds = _DEBOUNCE_MS / 1000.0

    def on_modified(self, event: FileModifiedEvent) -> None:
        if Path(event.src_path).resolve() != self._workflow_path.resolve():
            return

        self._last_event_time = time.monotonic()
        # 延迟执行防抖检查
        self._schedule_debounce()

    def _schedule_debounce(self) -> None:
        """防抖逻辑：在 _debounce_seconds 内无新事件时触发重新加载。"""
        # 使用简单的 sleep + 检查方式实现防抖
        # watchdog 事件在主线程回调中执行，此处用阻塞方式
        deadline = self._last_event_time + self._debounce_seconds

        while time.monotonic() < deadline:
            time.sleep(self._debounce_seconds / 2)
            # 如果有新事件，更新 deadline
            new_deadline = self._last_event_time + self._debounce_seconds
            if new_deadline > deadline:
                deadline = new_deadline

        self._do_reload()

    def _do_reload(self) -> None:
        """执行重新加载。"""
        try:
            wf = load_workflow(self._workflow_path)
            # 使用 resolver 中的逻辑验证配置
            from taolib.symphony.config.resolver import resolve_config

            config = resolve_config(
                cli_args={},
                toml_path=None,
                workflow_path=self._workflow_path,
            )
        except (WorkflowLoadError, ValueError) as exc:
            logger.warning(
                "工作流重新加载失败，保持最后有效配置: %s",
                exc,
            )
            if self._on_reload_error is not None:
                self._on_reload_error(exc)
            return

        self._last_valid_config = config
        logger.info(
            "工作流重新加载成功 (前置数据键: %s)",
            ", ".join(wf.config.keys()) or "(无)",
        )
        if self._on_reload_success is not None:
            self._on_reload_success(config)

    @property
    def last_valid_config(self) -> SymphonyConfig | None:
        """返回最后有效的配置。"""
        return self._last_valid_config


class WorkflowWatcher:
    """WORKFLOW.md 文件监视器。

    基于 watchdog 监视指定的工作流文件，变更时重新加载并验证配置。
    验证失败则保持最后有效配置，不会使服务崩溃。

    使用方式：

        watcher = WorkflowWatcher(
            workflow_path=Path("WORKFLOW.md"),
            on_reload_success=my_success_handler,
            on_reload_error=my_error_handler,
        )
        watcher.start()
        # ... 服务运行 ...
        watcher.stop()
    """

    def __init__(
        self,
        workflow_path: Path,
        on_reload_success: OnReloadSuccess | None = None,
        on_reload_error: OnReloadError | None = None,
    ) -> None:
        """初始化文件监视器。

        Args:
            workflow_path: 要监视的 WORKFLOW.md 文件路径。
            on_reload_success: 重新加载成功时的回调，接收新的 SymphonyConfig。
            on_reload_error: 重新加载失败时的回调，接收异常对象。
        """
        self._workflow_path = workflow_path.resolve()
        self._handler = _WorkflowEventHandler(
            workflow_path=self._workflow_path,
            on_reload_success=on_reload_success,
            on_reload_error=on_reload_error,
        )
        self._observer: Observer | None = None

    def start(self) -> None:
        """启动文件监视。"""
        if self._observer is not None:
            return

        self._observer = Observer()
        watch_dir = self._workflow_path.parent
        self._observer.schedule(
            self._handler,
            str(watch_dir),
            recursive=False,
        )
        self._observer.daemon = True
        self._observer.start()
        logger.info("文件监视已启动: %s", self._workflow_path)

    def stop(self) -> None:
        """停止文件监视。"""
        if self._observer is None:
            return

        self._observer.stop()
        self._observer.join(timeout=5.0)
        self._observer = None
        logger.info("文件监视已停止")

    @property
    def last_valid_config(self) -> SymphonyConfig | None:
        """返回最后有效的配置。"""
        return self._handler.last_valid_config
