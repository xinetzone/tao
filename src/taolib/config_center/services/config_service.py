"""配置业务逻辑服务模块。

实现配置管理的核心业务逻辑，包括 CRUD、缓存集成和事件发布。
"""
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from ..cache.config_cache import ConfigCacheProtocol
from ..events.types import ConfigChangedEvent
from ..models.config import ConfigCreate, ConfigResponse, ConfigUpdate
from ..models.enums import AuditAction, AuditStatus, ChangeType, ConfigStatus
from ..repository.config_repo import ConfigRepository
from ..services.audit_service import AuditService
from ..services.version_service import VersionService

if TYPE_CHECKING:
    from ..events.publisher import EventPublisher


class ConfigService:
    """配置业务逻辑服务。"""

    def __init__(
        self,
        config_repo: ConfigRepository,
        version_service: VersionService,
        audit_service: AuditService,
        cache: ConfigCacheProtocol,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        """初始化配置服务。

        Args:
            config_repo: 配置 Repository
            version_service: 版本服务
            audit_service: 审计服务
            cache: 配置缓存
            event_publisher: 事件发布器（可选）
        """
        self._config_repo = config_repo
        self._version_service = version_service
        self._audit_service = audit_service
        self._cache = cache
        self._event_publisher = event_publisher

    async def create_config(self, data: ConfigCreate, user_id: str) -> ConfigResponse:
        """创建配置。

        Args:
            data: 配置创建数据
            user_id: 用户 ID

        Returns:
            创建的配置响应
        """
        now = datetime.now(UTC)
        document = {
            "key": data.key,
            "environment": data.environment,
            "service": data.service,
            "value": data.value,
            "value_type": data.value_type,
            "description": data.description,
            "schema_id": data.schema_id,
            "tags": data.tags,
            "status": data.status,
            "version": 1,
            "created_by": user_id,
            "updated_by": user_id,
            "created_at": now,
            "updated_at": now,
        }

        config = await self._config_repo.create(document)

        # 创建初始版本
        await self._version_service.create_version(
            config_id=config.id,
            config_key=config.key,
            version=1,
            value=config.value,
            changed_by=user_id,
            change_type=ChangeType.CREATE,
            change_reason="初始创建",
        )

        # 记录审计日志
        await self._audit_service.log_action(
            action=AuditAction.CONFIG_CREATE,
            resource_type="config",
            resource_id=config.id,
            resource_key=config.key,
            actor_id=user_id,
            old_value=None,
            new_value=config.value,
            status=AuditStatus.SUCCESS,
        )

        # 发布配置变更事件
        await self._publish_event(
            config_id=config.id,
            config_key=config.key,
            environment=data.environment,
            service=data.service,
            change_type=ChangeType.CREATE,
            version=1,
            changed_by=user_id,
            new_value=config.value,
        )

        return config.to_response()

    async def get_config(self, config_id: str) -> ConfigResponse | None:
        """获取配置。

        Args:
            config_id: 配置 ID

        Returns:
            配置响应，如果不存在则返回 None
        """
        config = await self._config_repo.get_by_id(config_id)
        if config is None:
            return None
        return config.to_response()

    async def get_config_by_key_env_service(
        self,
        key: str,
        environment: str,
        service: str,
    ) -> ConfigResponse | None:
        """根据 key、环境和服务获取配置（优先从缓存）。

        Args:
            key: 配置键
            environment: 环境类型
            service: 服务名称

        Returns:
            配置响应，如果不存在则返回 None
        """
        # 尝试从缓存获取
        cached = await self._cache.get(environment, service, key)
        if cached is not None:
            return ConfigResponse(**cached)

        # 从数据库获取
        from ..models.enums import Environment

        config = await self._config_repo.find_by_key_env_service(
            key=key,
            environment=Environment(environment),
            service=service,
        )
        if config is None:
            return None

        response = config.to_response()

        # 写入缓存
        await self._cache.set(environment, service, key, response.model_dump())

        return response

    async def update_config(
        self,
        config_id: str,
        data: ConfigUpdate,
        user_id: str,
    ) -> ConfigResponse | None:
        """更新配置。

        Args:
            config_id: 配置 ID
            data: 配置更新数据
            user_id: 用户 ID

        Returns:
            更新后的配置响应，如果不存在则返回 None
        """
        config = await self._config_repo.get_by_id(config_id)
        if config is None:
            return None

        old_value = config.value
        updates = data.model_dump(exclude_unset=True)
        updates["updated_by"] = user_id
        updates["updated_at"] = datetime.now(UTC)
        updates["version"] = config.version + 1

        updated_config = await self._config_repo.update(config_id, updates)
        if updated_config is None:
            return None

        # 创建新版本
        await self._version_service.create_version(
            config_id=config_id,
            config_key=updated_config.key,
            version=updated_config.version,
            value=updated_config.value,
            changed_by=user_id,
            change_type=ChangeType.UPDATE,
            change_reason="配置更新",
        )

        # 删除缓存
        await self._cache.delete(
            updated_config.environment,
            updated_config.service,
            updated_config.key,
        )

        # 记录审计日志
        await self._audit_service.log_action(
            action=AuditAction.CONFIG_UPDATE,
            resource_type="config",
            resource_id=config_id,
            resource_key=updated_config.key,
            actor_id=user_id,
            old_value=old_value,
            new_value=updated_config.value,
            status=AuditStatus.SUCCESS,
        )

        return updated_config.to_response()

    async def delete_config(self, config_id: str, user_id: str) -> bool:
        """删除配置。

        Args:
            config_id: 配置 ID
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        config = await self._config_repo.get_by_id(config_id)
        if config is None:
            return False

        deleted = await self._config_repo.delete(config_id)

        if deleted:
            # 删除缓存
            await self._cache.delete(config.environment, config.service, config.key)

            # 记录审计日志
            await self._audit_service.log_action(
                action=AuditAction.CONFIG_DELETE,
                resource_type="config",
                resource_id=config_id,
                resource_key=config.key,
                actor_id=user_id,
                old_value=config.value,
                new_value=None,
                status=AuditStatus.SUCCESS,
            )

        return deleted

    async def publish_config(
        self, config_id: str, user_id: str
    ) -> ConfigResponse | None:
        """发布配置（draft → active）。

        Args:
            config_id: 配置 ID
            user_id: 用户 ID

        Returns:
            发布后的配置响应，如果不存在则返回 None
        """
        config = await self._config_repo.get_by_id(config_id)
        if config is None:
            return None

        updates = {
            "status": ConfigStatus.ACTIVE,
            "updated_by": user_id,
            "updated_at": datetime.now(UTC),
        }

        updated_config = await self._config_repo.update(config_id, updates)
        if updated_config is None:
            return None

        # 删除缓存
        await self._cache.delete(
            updated_config.environment, updated_config.service, updated_config.key
        )

        # 记录审计日志
        await self._audit_service.log_action(
            action=AuditAction.CONFIG_PUBLISH,
            resource_type="config",
            resource_id=config_id,
            resource_key=updated_config.key,
            actor_id=user_id,
            old_value=ConfigStatus.DRAFT,
            new_value=ConfigStatus.ACTIVE,
            status=AuditStatus.SUCCESS,
        )

        # 发布配置变更事件
        await self._publish_event(
            config_id=config_id,
            config_key=updated_config.key,
            environment=updated_config.environment,
            service=updated_config.service,
            change_type="publish",
            version=updated_config.version,
            changed_by=user_id,
            new_value=updated_config.value,
        )

        return updated_config.to_response()

    async def list_configs(
        self,
        environment: str | None = None,
        service: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConfigResponse]:
        """查询配置列表。

        Args:
            environment: 环境过滤
            service: 服务过滤
            status: 状态过滤
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            配置响应列表
        """
        from ..models.enums import ConfigStatus as CS
        from ..models.enums import Environment

        filters: dict[str, Any] = {}
        if environment:
            filters["environment"] = Environment(environment)
        if service:
            filters["service"] = service
        if status:
            filters["status"] = CS(status)

        configs = await self._config_repo.list(filters=filters, skip=skip, limit=limit)
        return [config.to_response() for config in configs]

    # ------------------------------------------------------------------
    # 事件发布辅助
    # ------------------------------------------------------------------

    async def _publish_event(
        self,
        *,
        config_id: str,
        config_key: str,
        environment: str,
        service: str,
        change_type: str | ChangeType,
        version: int,
        changed_by: str,
        new_value: Any = None,
    ) -> None:
        """发布配置变更事件（若事件发布器可用）。"""
        if self._event_publisher is None:
            return
        event = ConfigChangedEvent(
            config_id=config_id,
            config_key=config_key,
            environment=str(environment),
            service=str(service),
            change_type=str(change_type),
            version=version,
            changed_by=changed_by,
            timestamp=datetime.now(UTC),
            new_value=new_value,
        )
        await self._event_publisher.publish_config_changed(event)

    async def rollback_config(
        self,
        config_id: str,
        version_num: int,
        user_id: str,
    ) -> ConfigResponse | None:
        """回滚配置到指定版本。

        将配置值恢复为目标版本的值，同时创建回滚版本记录、
        更新配置文档、清除缓存并记录审计日志。

        Args:
            config_id: 配置 ID
            version_num: 目标版本号
            user_id: 操作用户 ID

        Returns:
            回滚后的配置响应，如果配置或版本不存在则返回 None
        """
        config = await self._config_repo.get_by_id(config_id)
        if config is None:
            return None

        old_value = config.value

        # 通过 VersionService 创建回滚版本记录
        rollback_version = await self._version_service.rollback_to_version(
            config_id=config_id,
            version_num=version_num,
            user_id=user_id,
        )
        if rollback_version is None:
            return None

        # 更新配置文档的值为目标版本的值
        updates = {
            "value": rollback_version.value,
            "version": rollback_version.version,
            "updated_by": user_id,
            "updated_at": datetime.now(UTC),
        }
        updated_config = await self._config_repo.update(config_id, updates)
        if updated_config is None:
            return None

        # 删除缓存
        await self._cache.delete(
            updated_config.environment,
            updated_config.service,
            updated_config.key,
        )

        # 记录审计日志
        await self._audit_service.log_action(
            action=AuditAction.CONFIG_ROLLBACK,
            resource_type="config",
            resource_id=config_id,
            resource_key=updated_config.key,
            actor_id=user_id,
            old_value=old_value,
            new_value=rollback_version.value,
            status=AuditStatus.SUCCESS,
        )

        # 发布配置变更事件
        await self._publish_event(
            config_id=config_id,
            config_key=updated_config.key,
            environment=updated_config.environment,
            service=updated_config.service,
            change_type=ChangeType.ROLLBACK,
            version=updated_config.version,
            changed_by=user_id,
            new_value=rollback_version.value,
        )

        return updated_config.to_response()
