"""数据同步管道模块。

MongoDB 到 MongoDB 的数据同步管道，支持：
- 增量/全量同步
- 自定义 Python 转换函数
- 检查点恢复
- 失败记录追踪
- 定时/手动触发

使用方式：

    from taolib.data_sync.services import SyncOrchestrator, SyncJobService
    from taolib.data_sync.repository import SyncJobRepository

    # 创建服务
    job_service = SyncJobService(job_repo)
    orchestrator = SyncOrchestrator(...)

    # 运行同步作业
    log = await orchestrator.run_job(job_id)

启动 Web 服务器：

    from taolib.data_sync.server.app import create_app

    app = create_app()
    # 使用 uvicorn.run(app, host="0.0.0.0", port=8001)
"""

from taolib.data_sync.errors import (
    SyncAbortError,
    SyncCheckpointError,
    SyncConnectionError,
    SyncError,
    SyncJobNotFoundError,
    SyncTransformError,
)
from taolib.data_sync.models import (
    FailureAction,
    FailureRecordDocument,
    SyncCheckpoint,
    SyncConnectionConfig,
    SyncJobCreate,
    SyncJobDocument,
    SyncJobResponse,
    SyncJobUpdate,
    SyncLogCreate,
    SyncLogDocument,
    SyncLogResponse,
    SyncMetrics,
    SyncMode,
    SyncScope,
    SyncStatus,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Errors
    "SyncError",
    "SyncJobNotFoundError",
    "SyncConnectionError",
    "SyncTransformError",
    "SyncCheckpointError",
    "SyncAbortError",
    # Models
    "SyncStatus",
    "SyncScope",
    "SyncMode",
    "FailureAction",
    "SyncConnectionConfig",
    "SyncJobCreate",
    "SyncJobUpdate",
    "SyncJobResponse",
    "SyncJobDocument",
    "SyncMetrics",
    "SyncLogCreate",
    "SyncLogResponse",
    "SyncLogDocument",
    "SyncCheckpoint",
    "FailureRecordDocument",
]
