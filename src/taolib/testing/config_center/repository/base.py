"""泛型 Repository 基类模块。

向后兼容重导出：实际实现已迁移至 ``taolib._base.repository``。
"""

from taolib.testing._base.repository import AsyncRepository

__all__ = ["AsyncRepository"]


