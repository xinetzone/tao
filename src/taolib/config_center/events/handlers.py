"""事件处理器模块。

处理配置变更事件，执行缓存失效、审计等操作。
"""

from ..cache.config_cache import ConfigCacheProtocol
from ..events.types import ConfigChangedEvent
from ..services.audit_service import AuditService


class ConfigChangedHandler:
    """配置变更事件处理器。"""

    def __init__(
        self,
        cache: ConfigCacheProtocol,
        audit_service: AuditService,
    ) -> None:
        """初始化处理器。

        Args:
            cache: 配置缓存
            audit_service: 审计服务
        """
        self._cache = cache
        self._audit_service = audit_service

    async def handle(self, event: ConfigChangedEvent) -> None:
        """处理配置变更事件。

        Args:
            event: 配置变更事件
        """
        # 删除缓存
        await self._cache.delete(event.environment, event.service, event.config_key)
