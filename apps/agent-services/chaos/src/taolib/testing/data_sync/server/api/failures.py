"""同步失败记录路由。"""

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

router = APIRouter(tags=["Failures"])


def get_failure_repo(request: Request):
    """获取失败记录 Repository。"""
    from ...repository.failure_repo import FailureRecordRepository

    return FailureRecordRepository(request.app.state.db.sync_failures)


class FailureListResponse(BaseModel):
    """失败记录列表响应。"""

    items: list[dict[str, Any]]
    total: int


@router.get("", response_model=FailureListResponse)
async def list_failures(
    request: Request,
    job_id: str | None = None,
    log_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> FailureListResponse:
    """查询失败记录。"""
    repo = get_failure_repo(request)

    if log_id:
        records = await repo.find_by_log(log_id, skip=skip, limit=limit)
    elif job_id:
        records = await repo.list(
            filters={"job_id": job_id},
            skip=skip,
            limit=limit,
        )
    else:
        records = await repo.list(skip=skip, limit=limit)

    items = [r.model_dump(by_alias=True) for r in records]
    return FailureListResponse(items=items, total=len(items))


@router.get("/{failure_id}")
async def get_failure(
    request: Request,
    failure_id: str,
) -> dict[str, Any]:
    """获取单条失败记录。"""
    repo = get_failure_repo(request)
    record = await repo.get_by_id(failure_id)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failure record not found: {failure_id}",
        )

    return record.model_dump(by_alias=True)
