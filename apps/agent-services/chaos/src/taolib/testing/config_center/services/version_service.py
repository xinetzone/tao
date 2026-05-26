"""版本管理服务模块。

实现配置版本历史、回滚和差异比较功能。
"""

from datetime import UTC, datetime
from typing import Any

from ..models.enums import ChangeType
from ..models.version import ConfigVersionResponse
from ..repository.version_repo import VersionRepository
from ..services.audit_service import AuditService


class VersionService:
    """版本业务逻辑服务。"""

    def __init__(
        self,
        version_repo: VersionRepository,
        audit_service: AuditService,
    ) -> None:
        """初始化版本服务。

        Args:
            version_repo: 版本 Repository
            audit_service: 审计服务
        """
        self._version_repo = version_repo
        self._audit_service = audit_service

    async def create_version(
        self,
        config_id: str,
        config_key: str,
        version: int,
        value: Any,
        changed_by: str,
        change_type: ChangeType,
        change_reason: str = "",
        diff_summary: dict[str, Any] | None = None,
    ) -> ConfigVersionResponse:
        """创建配置版本。

        Args:
            config_id: 配置 ID
            config_key: 配置键
            version: 版本号
            value: 配置值
            changed_by: 变更人用户 ID
            change_type: 变更类型
            change_reason: 变更原因
            diff_summary: 差异摘要

        Returns:
            创建的版本响应
        """
        document = {
            "config_id": config_id,
            "config_key": config_key,
            "version": version,
            "value": value,
            "changed_by": changed_by,
            "change_reason": change_reason,
            "change_type": change_type,
            "diff_summary": diff_summary,
            "is_rollback_target": False,
            "created_at": datetime.now(UTC),
        }

        version_doc = await self._version_repo.create(document)
        return version_doc.to_response()

    async def get_versions(
        self,
        config_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ConfigVersionResponse]:
        """获取配置版本历史。

        Args:
            config_id: 配置 ID
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            版本响应列表
        """
        versions = await self._version_repo.get_versions_by_config(
            config_id=config_id,
            skip=skip,
            limit=limit,
        )
        return [v.to_response() for v in versions]

    async def get_version(
        self,
        config_id: str,
        version_num: int,
    ) -> ConfigVersionResponse | None:
        """获取指定版本。

        Args:
            config_id: 配置 ID
            version_num: 版本号

        Returns:
            版本响应，如果不存在则返回 None
        """
        version = await self._version_repo.get_version(config_id, version_num)
        if version is None:
            return None
        return version.to_response()

    async def rollback_to_version(
        self,
        config_id: str,
        version_num: int,
        user_id: str,
    ) -> ConfigVersionResponse | None:
        """回滚到指定版本。

        Args:
            config_id: 配置 ID
            version_num: 目标版本号
            user_id: 操作用户 ID

        Returns:
            回滚后的版本响应，如果版本不存在则返回 None
        """
        target_version = await self._version_repo.get_version(config_id, version_num)
        if target_version is None:
            return None

        # 获取最新版本号
        latest_version = await self._version_repo.get_latest_version(config_id)
        new_version_num = latest_version + 1

        # 创建回滚版本
        rollback_version = await self.create_version(
            config_id=config_id,
            config_key=target_version.config_key,
            version=new_version_num,
            value=target_version.value,
            changed_by=user_id,
            change_type=ChangeType.ROLLBACK,
            change_reason=f"回滚到版本 {version_num}",
        )

        # 标记回滚目标
        await self._version_repo.update(
            target_version.id,
            {"is_rollback_target": True},
        )

        return rollback_version

    async def compare_versions(
        self,
        config_id: str,
        v1: int,
        v2: int,
    ) -> dict[str, Any] | None:
        """比较两个版本的差异。

        Args:
            config_id: 配置 ID
            v1: 版本1
            v2: 版本2

        Returns:
            差异摘要字典，如果任一版本不存在则返回 None
        """
        version1 = await self._version_repo.get_version(config_id, v1)
        version2 = await self._version_repo.get_version(config_id, v2)

        if version1 is None or version2 is None:
            return None

        return {
            "version_1": v1,
            "version_2": v2,
            "value_1": version1.value,
            "value_2": version2.value,
            "changed_by_1": version1.changed_by,
            "changed_by_2": version2.changed_by,
            "change_type_1": version1.change_type,
            "change_type_2": version2.change_type,
        }


