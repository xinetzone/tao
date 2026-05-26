"""Tracker 子包 — Issue Tracker 客户端抽象与实现。

提供统一的 :class:`TrackerClient` 接口和 Linear 具体实现，
供编排层通过依赖反转访问外部 issue 跟踪器。
"""

from taolib.symphony.tracker.base import TrackerClient
from taolib.symphony.tracker.errors import (
    LinearAPIRequestError,
    LinearAPIStatusError,
    LinearError,
    LinearGraphQLError,
    LinearMissingCursorError,
)
from taolib.symphony.tracker.linear import LinearClient
from taolib.symphony.tracker.models import Issue, TrackerConfig

__all__ = [
    # 抽象
    "TrackerClient",
    # 实现
    "LinearClient",
    # 模型
    "Issue",
    "TrackerConfig",
    # 异常
    "LinearError",
    "LinearAPIRequestError",
    "LinearAPIStatusError",
    "LinearGraphQLError",
    "LinearMissingCursorError",
]
