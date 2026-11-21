"""字体子系统的异常类型。"""

__all__ = ["FontConfigError"]


class FontConfigError(RuntimeError):
    """字体目录缺失、没有可用字体，或目标家族无法解析。"""
