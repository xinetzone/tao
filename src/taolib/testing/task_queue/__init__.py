"""后台任务队列模块。

基于 Redis 的后台任务处理系统，支持：
- 三级优先级队列（高/普通/低）
- 失败自动重试（递增延迟）
- 可配置的并发 Worker
- MongoDB 持久化任务记录
- Web 管理仪表板

使用方式：

    from taolib.testing.task_queue import TaskCreate, TaskPriority
    from taolib.testing.task_queue.services.task_service import TaskService
    from taolib.testing.task_queue.worker.registry import task_handler

    # 注册任务处理器
    @task_handler("send_email")
    async def handle_send_email(params: dict) -> dict:
        await send_email(params["to"], params["subject"])
        return {"sent": True}

    # 提交任务
    task = await task_service.submit_task(
        TaskCreate(task_type="send_email", params={"to": "user@example.com"})
    )

启动 Web 服务器：

    from taolib.testing.task_queue.server.app import create_app

    app = create_app()
    # 使用 uvicorn.run(app, host="0.0.0.0", port=8002)
"""

from taolib.testing.task_queue.errors import (
    TaskAlreadyExistsError,
    TaskExecutionError,
    TaskHandlerNotFoundError,
    TaskMaxRetriesExceededError,
    TaskNotFoundError,
    TaskQueueConnectionError,
    TaskQueueError,
)
from taolib.testing.task_queue.models import (
    TaskCreate,
    TaskDocument,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Errors
    "TaskQueueError",
    "TaskNotFoundError",
    "TaskAlreadyExistsError",
    "TaskHandlerNotFoundError",
    "TaskExecutionError",
    "TaskQueueConnectionError",
    "TaskMaxRetriesExceededError",
    # Models
    "TaskStatus",
    "TaskPriority",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskDocument",
]


