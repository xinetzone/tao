"""taolib - 实用工具库

该模块提供了一系列实用工具函数和类，用于各种日常开发任务。
"""
# 导入版本模块
try:
    from .version import __version__, get_version
except ImportError:
    # 如果版本模块不可用，设置默认版本号
    __version__ = "0.0.0"

    def get_version(package_name: str = "taolib", fallback: str = "0.0.0") -> str:
        return fallback

__all__ = ["__version__", "get_version", "doc"]
