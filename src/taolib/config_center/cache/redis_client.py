"""Redis 客户端管理模块。

向后兼容重导出：实际实现已迁移至 ``taolib._base.redis_pool``。
"""

from taolib._base.redis_pool import close_redis_client, get_redis_client

__all__ = ["close_redis_client", "get_redis_client"]
