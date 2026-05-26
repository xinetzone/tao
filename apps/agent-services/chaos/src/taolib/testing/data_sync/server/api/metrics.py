"""同步指标路由。"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["Metrics"])


def get_metrics_service(request: Request):
    """获取指标服务。"""
    from ...repository.checkpoint_repo import CheckpointRepository
    from ...repository.failure_repo import FailureRecordRepository
    from ...repository.log_repo import SyncLogRepository
    from ...services.metrics_service import MetricsService

    return MetricsService(
        log_repo=SyncLogRepository(request.app.state.db.sync_logs),
        failure_repo=FailureRecordRepository(request.app.state.db.sync_failures),
        checkpoint_repo=CheckpointRepository(request.app.state.db.sync_checkpoints),
    )


class GlobalMetricsResponse(BaseModel):
    """全局指标响应。"""

    total_jobs: int
    recent_runs: int
    completed: int
    failed: int


@router.get("", response_model=GlobalMetricsResponse)
async def get_global_metrics(request: Request) -> GlobalMetricsResponse:
    """获取全局同步指标。"""
    svc = get_metrics_service(request)
    summary = await svc.get_global_summary()
    return GlobalMetricsResponse(**summary)


@router.get("/{job_id}")
async def get_job_metrics(request: Request, job_id: str) -> dict[str, Any]:
    """获取指定作业的指标摘要。"""
    svc = get_metrics_service(request)
    return await svc.get_job_summary(job_id)


@router.get("/{job_id}/failures")
async def get_job_failure_summary(
    request: Request,
    job_id: str,
) -> dict[str, Any]:
    """获取指定作业的失败统计。"""
    svc = get_metrics_service(request)
    return await svc.get_failure_summary(job_id)


