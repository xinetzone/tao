"""共享基础模块。

提供跨模块复用的基础设施组件：泛型 Repository 基类和 Redis 连接池管理。
"""

from taolib.testing._base.redis_pool import close_redis_client, get_redis_client
from taolib.testing._base.repository import AsyncRepository

__all__ = [
    "AsyncRepository",
    "close_redis_client",
    "get_redis_client",
]


