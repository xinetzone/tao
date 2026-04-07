"""同步指标服务。

提供聚合统计和监控数据查询。
"""

import logging
from typing import Any

from taolib.data_sync.repository.checkpoint_repo import CheckpointRepository
from taolib.data_sync.repository.failure_repo import FailureRecordRepository
from taolib.data_sync.repository.log_repo import SyncLogRepository

logger = logging.getLogger(__name__)


class MetricsService:
    """同步指标服务。"""

    def __init__(
        self,
        log_repo: SyncLogRepository,
        failure_repo: FailureRecordRepository,
        checkpoint_repo: CheckpointRepository | None = None,
    ) -> None:
        """初始化。

        Args:
            log_repo: 日志 Repository
            failure_repo: 失败记录 Repository
            checkpoint_repo: 检查点 Repository（可选）
        """
        self._log_repo = log_repo
        self._failure_repo = failure_repo
        self._checkpoint_repo = checkpoint_repo

    async def get_job_summary(self, job_id: str) -> dict[str, Any]:
        """获取作业摘要。

        Args:
            job_id: 作业 ID

        Returns:
            作业摘要字典
        """
        logs = await self._log_repo.find_by_job(job_id, limit=10)
        aggregate = await self._log_repo.get_aggregate_metrics(job_id)

        # 计算成功率
        total_runs = len(logs)
        success_runs = sum(1 for log in logs if log.status == "completed")
        success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0

        summary: dict[str, Any] = {
            "job_id": job_id,
            "total_runs": total_runs,
            "success_runs": success_runs,
            "success_rate": round(success_rate, 2),
            "aggregate_metrics": aggregate,
            "recent_logs": [log.to_response() for log in logs[:5]],
        }

        # 添加检查点信息
        if self._checkpoint_repo:
            checkpoints = await self._checkpoint_repo.list(
                filters={"job_id": job_id},
            )
            summary["checkpoints"] = [
                {
                    "collection_name": cp.collection_name,
                    "last_synced_timestamp": cp.last_synced_timestamp.isoformat()
                    if cp.last_synced_timestamp
                    else None,
                    "total_synced": cp.total_synced,
                    "updated_at": cp.updated_at.isoformat(),
                }
                for cp in checkpoints
            ]

        return summary

    async def get_global_summary(self) -> dict[str, Any]:
        """获取全局摘要。

        Returns:
            全局摘要字典
        """
        recent_logs = await self._log_repo.find_recent(limit=50)
        total_jobs = len(set(log.job_id for log in recent_logs))
        completed = sum(1 for log in recent_logs if log.status == "completed")
        failed = sum(1 for log in recent_logs if log.status == "failed")

        return {
            "total_jobs": total_jobs,
            "recent_runs": len(recent_logs),
            "completed": completed,
            "failed": failed,
        }

    async def get_failure_summary(self, job_id: str) -> dict[str, Any]:
        """获取失败统计。

        Args:
            job_id: 作业 ID

        Returns:
            失败统计字典
        """
        total_failures = await self._failure_repo.count_by_job(job_id)
        return {
            "job_id": job_id,
            "total_failures": total_failures,
        }
