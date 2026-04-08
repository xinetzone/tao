"""同步作业服务。

提供 SyncJob 的 CRUD 操作和业务逻辑。
"""

import logging
from datetime import UTC, datetime
from typing import Any

from taolib.testing.data_sync.errors import SyncJobNotFoundError
from taolib.testing.data_sync.models.job import SyncJobCreate, SyncJobDocument, SyncJobUpdate
from taolib.testing.data_sync.repository.job_repo import SyncJobRepository

logger = logging.getLogger(__name__)


class SyncJobService:
    """同步作业服务。"""

    def __init__(self, job_repo: SyncJobRepository) -> None:
        """初始化。

        Args:
            job_repo: 同步作业 Repository
        """
        self._job_repo = job_repo

    async def create_job(
        self,
        job_create: SyncJobCreate,
        user_id: str = "system",
    ) -> SyncJobDocument:
        """创建同步作业。

        Args:
            job_create: 作业创建数据
            user_id: 用户 ID

        Returns:
            创建的作业文档
        """
        doc_data = job_create.model_dump(by_alias=False)
        doc_data["_id"] = job_create.name  # 使用 name 作为 _id
        doc_data["created_by"] = user_id
        doc_data["updated_by"] = user_id
        doc_data["created_at"] = datetime.now(UTC)
        doc_data["updated_at"] = datetime.now(UTC)
        logger.info("创建同步作业: %s (user=%s)", job_create.name, user_id)
        return await self._job_repo.create(doc_data)

    async def get_job(self, job_id: str) -> SyncJobDocument:
        """获取作业详情。

        Args:
            job_id: 作业 ID

        Returns:
            作业文档

        Raises:
            SyncJobNotFoundError: 如果作业不存在
        """
        job = await self._job_repo.get_by_id(job_id)
        if job is None:
            raise SyncJobNotFoundError(f"Job not found: {job_id}")
        return job

    async def update_job(
        self,
        job_id: str,
        job_update: SyncJobUpdate,
        user_id: str = "system",
    ) -> SyncJobDocument:
        """更新作业配置。

        Args:
            job_id: 作业 ID
            job_update: 更新数据
            user_id: 用户 ID

        Returns:
            更新后的作业文档

        Raises:
            SyncJobNotFoundError: 如果作业不存在
        """
        # 确保作业存在
        await self.get_job(job_id)

        updates = job_update.model_dump(exclude_none=True, by_alias=False)
        if updates:
            updates["updated_by"] = user_id
            updates["updated_at"] = datetime.now(UTC)
            result = await self._job_repo.update(job_id, updates)
            if result is None:
                raise SyncJobNotFoundError(f"Failed to update job: {job_id}")
            return result
        return await self.get_job(job_id)

    async def delete_job(self, job_id: str) -> bool:
        """删除作业。

        Args:
            job_id: 作业 ID

        Returns:
            是否删除成功
        """
        logger.info("删除同步作业: %s", job_id)
        return await self._job_repo.delete(job_id)

    async def list_jobs(
        self,
        enabled_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SyncJobDocument]:
        """列出作业。

        Args:
            enabled_only: 只返回启用的作业
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            作业文档列表
        """
        if enabled_only:
            return await self._job_repo.find_enabled_jobs()
        return await self._job_repo.list(skip=skip, limit=limit)

    async def enable_job(self, job_id: str, user_id: str = "system") -> SyncJobDocument:
        """启用作业。"""
        return await self.update_job(
            job_id,
            SyncJobUpdate(enabled=True),
            user_id,
        )

    async def disable_job(
        self, job_id: str, user_id: str = "system"
    ) -> SyncJobDocument:
        """禁用作业。"""
        return await self.update_job(
            job_id,
            SyncJobUpdate(enabled=False),
            user_id,
        )

    async def reset_checkpoint(
        self,
        job_id: str,
        checkpoint_repo: Any,  # CheckpointRepository
    ) -> int:
        """重置作业检查点（强制下次全量同步）。

        Args:
            job_id: 作业 ID
            checkpoint_repo: 检查点 Repository

        Returns:
            删除的检查点数量
        """
        await self.get_job(job_id)  # 验证作业存在
        return await checkpoint_repo.delete_by_job(job_id)


