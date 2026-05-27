"""审计日志 API 模块。

实现审计日志查询的 RESTful API 端点。
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from ...models.audit import AuditLogResponse
from ...repository.audit_repo import AuditLogRepository
from ..dependencies import get_audit_repo, get_current_user

router = APIRouter(prefix="/audit/logs", tags=["审计日志"])


@router.get("", response_model=list[AuditLogResponse])
async def query_audit_logs(
    resource_type: str | None = Query(default=None),
    resource_id: str | None = Query(default=None),
    actor_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    current_user=Depends(get_current_user),
) -> list[AuditLogResponse]:
    """查询审计日志。

    Args:
        resource_type: 资源类型筛选
        resource_id: 资源 ID 筛选
        actor_id: 操作者 ID 筛选
        action: 操作类型筛选
        skip: 跳过记录数
        limit: 限制记录数
        audit_repo: 审计日志 Repository
        current_user: 当前用户

    Returns:
        审计日志列表
    """
    # 构建查询条件
    filters: dict = {}
    if resource_type:
        filters["resource_type"] = resource_type
    if resource_id:
        filters["resource_id"] = resource_id
    if actor_id:
        filters["actor_id"] = actor_id
    if action:
        filters["action"] = action

    logs = await audit_repo.query_logs(
        filters=filters if filters else None,
        skip=skip,
        limit=limit,
    )
    return [AuditLogResponse(**log.model_dump()) for log in logs]


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: str,
    audit_repo: AuditLogRepository = Depends(get_audit_repo),
    current_user=Depends(get_current_user),
) -> AuditLogResponse:
    """获取审计日志详情。

    Args:
        log_id: 日志 ID
        audit_repo: 审计日志 Repository
        current_user: 当前用户

    Returns:
        审计日志详情

    Raises:
        HTTPException: 如果日志不存在
    """
    log = await audit_repo.get_by_id(log_id)
    if log is None:
        raise HTTPException(
            status_code=404,
            detail="审计日志不存在",
        )
    return AuditLogResponse(**log.model_dump())
