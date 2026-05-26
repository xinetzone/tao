"""同步日志路由。"""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ...models import SyncLogResponse

router = APIRouter(tags=["Logs"])


def get_log_repo(request: Request):
    """获取日志 Repository。"""
    from ...repository.log_repo import SyncLogRepository

    return SyncLogRepository(request.app.state.db.sync_logs)


class LogListResponse(BaseModel):
    """日志列表响应。"""

    items: list[SyncLogResponse]
    total: int


@router.get("", response_model=LogListResponse)
async def list_logs(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    job_id: str | None = None,
    status: str | None = None,
) -> LogListResponse:
    """列出同步日志。"""
    repo = get_log_repo(request)

    # 简化实现，实际应支持更复杂的过滤
    if job_id:
        logs = await repo.find_by_job(job_id, skip=skip, limit=limit)
    else:
        logs = await repo.find_recent(limit=limit)

    return LogListResponse(
        items=[log.to_response() for log in logs],
        total=len(logs),
    )


@router.get("/{log_id}", response_model=SyncLogResponse)
async def get_log(request: Request, log_id: str) -> SyncLogResponse:
    """获取指定日志。"""
    repo = get_log_repo(request)
    log = await repo.get_by_id(log_id)

    if log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Log not found: {log_id}",
        )

    return log.to_response()


