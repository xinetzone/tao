"""开发工具层：检查、回放与性能剖析。

* :mod:`.inspector` - 实时状态检查器；
* :mod:`.replay` - 执行回放工具；
* :mod:`.profiler` - 性能剖析器与热点分析。
"""

from __future__ import annotations

from .inspector import (
    InspectorConfig,
    StateDiff,
    StateInspector,
    WatchCallback,
    format_state_tree,
)
from .profiler import (
    HotspotAnalyzer,
    HotspotEntry,
    PerformanceProfiler,
    ProfileConfig,
    ProfileResult,
    ProfileSample,
    profiled,
)
from .replay import (
    ExecutionRecording,
    RecordedEvent,
    ReplayCallback,
    ReplayConfig,
    ReplayEngine,
    ReplayEventType,
    ReplayMode,
)

__all__ = [
    "ExecutionRecording",
    "HotspotAnalyzer",
    "HotspotEntry",
    "InspectorConfig",
    "PerformanceProfiler",
    "ProfileConfig",
    "ProfileResult",
    "ProfileSample",
    "RecordedEvent",
    "ReplayCallback",
    "ReplayConfig",
    "ReplayEngine",
    "ReplayEventType",
    "ReplayMode",
    "StateDiff",
    "StateInspector",
    "WatchCallback",
    "format_state_tree",
    "profiled",
]
