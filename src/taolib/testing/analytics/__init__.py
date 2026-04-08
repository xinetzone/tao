"""用户行为分析模块。

提供用户行为追踪和分析功能，支持：
- 页面浏览和点击追踪
- 功能使用情况分析
- 用户导航路径追踪
- 区域停留时间统计
- 关键流程流失点分析

使用方式：

    from taolib.testing.analytics.models import EventCreate, EventType
    from taolib.testing.analytics.services import AnalyticsService

    # 通过 AnalyticsService 摄入事件
    service = AnalyticsService(event_repo, session_repo)
    result = await service.ingest_events(events)

启动 Web 服务器：

    from taolib.testing.analytics.server.app import create_app

    app = create_app()
    # 使用 uvicorn.run(app, host="0.0.0.0", port=8002)
"""

from taolib.testing.analytics.errors import (
    AggregationError,
    AnalyticsError,
    AppNotFoundError,
    EventValidationError,
)
from taolib.testing.analytics.models import (
    DeviceType,
    EventBase,
    EventBatchCreate,
    EventCreate,
    EventDocument,
    EventResponse,
    EventType,
    SessionDocument,
)

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Errors
    "AnalyticsError",
    "EventValidationError",
    "AppNotFoundError",
    "AggregationError",
    # Enums
    "EventType",
    "DeviceType",
    # Models
    "EventBase",
    "EventCreate",
    "EventBatchCreate",
    "EventResponse",
    "EventDocument",
    "SessionDocument",
]


