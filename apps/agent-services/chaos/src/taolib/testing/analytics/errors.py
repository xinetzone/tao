"""分析模块异常定义。

定义分析模块中的自定义异常。
"""


class AnalyticsError(Exception):
    """分析模块基础异常。"""


class EventValidationError(AnalyticsError):
    """事件数据验证错误。"""


class AppNotFoundError(AnalyticsError):
    """未知的应用标识。"""


class AggregationError(AnalyticsError):
    """MongoDB 聚合管道执行失败。"""
