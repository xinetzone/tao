"""用户行为分析枚举类型。

定义分析模块中使用的各种枚举。
"""

from enum import StrEnum


class EventType(StrEnum):
    """事件类型。"""

    PAGE_VIEW = "page_view"
    CLICK = "click"
    FEATURE_USE = "feature_use"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    NAVIGATION = "navigation"
    TIME_ON_SECTION = "time_on_section"
    CUSTOM = "custom"


class DeviceType(StrEnum):
    """设备类型。"""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"


